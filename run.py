#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import yaml

from event_pipeline.analysis import Analyzer
from event_pipeline.config import (
    load_project_config,
    load_sources,
    merge_and_save_candidate_sources,
)
from event_pipeline.dedupe import deduplicate_events
from event_pipeline.enrich import enrich_candidate_from_detail
from event_pipeline.export_portal import export_portal_payload
from event_pipeline.fetch import Fetcher
from event_pipeline.parsing import discover_candidate_sources, extract_candidate_events
from event_pipeline.providers import create_provider
from event_pipeline.render_html import render_events_html
from eventgen_engine.catalog import load_area_catalog, resolve_area
from eventgen_engine.generator import create_generated_configs


REPO_ROOT = Path(__file__).resolve().parent
AREA_CATALOG_DIR = REPO_ROOT / "catalog" / "areas"
DEFAULT_GENERATED_ROOT = REPO_ROOT / "generated"


def build_parser():
    parser = argparse.ArgumentParser(
        description="EventGEn: motore locale per generare fonti compatibili e analizzare eventi pubblici."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Esegue la pipeline di analisi eventi.")
    _add_analyze_arguments(analyze_parser)

    list_parser = subparsers.add_parser("list-areas", help="Mostra le aree catalogate nel motore.")
    list_parser.add_argument(
        "--catalog",
        default=str(AREA_CATALOG_DIR),
        help="Cartella contenente il catalogo aree.",
    )

    resolve_parser = subparsers.add_parser("resolve-area", help="Risolve una query area e stampa o salva la definizione.")
    resolve_parser.add_argument("--query", required=True, help="Nome area, alias o zona.")
    resolve_parser.add_argument("--catalog", default=str(AREA_CATALOG_DIR), help="Cartella catalogo aree.")
    resolve_parser.add_argument("--output", default="", help="Salva l'area risolta in un file YAML.")

    generate_parser = subparsers.add_parser(
        "generate-config",
        help="Genera area.yaml, project.yaml, sources.yaml e sources_candidates.yaml da un'area.",
    )
    _add_generation_arguments(generate_parser)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Genera la configurazione per un'area e lancia subito la pipeline di analisi.",
    )
    _add_generation_arguments(bootstrap_parser)
    bootstrap_parser.add_argument(
        "--provider",
        default="none",
        choices=["none", "openai", "claude", "gemini"],
        help="Provider IA opzionale.",
    )
    bootstrap_parser.add_argument(
        "--max-sources",
        type=int,
        default=6,
        help="Numero massimo di fonti da processare nel bootstrap di test.",
    )

    return parser


def _add_analyze_arguments(parser):
    parser.add_argument(
        "--provider",
        default="none",
        choices=["none", "openai", "claude", "gemini"],
        help="Provider IA opzionale per analisi e classificazione.",
    )
    parser.add_argument("--project", default="project.yaml", help="Percorso del file project.yaml")
    parser.add_argument("--sources", default="sources.yaml", help="Percorso del file sources.yaml")
    parser.add_argument(
        "--candidates",
        default="sources_candidates.yaml",
        help="Percorso del file sources_candidates.yaml",
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Limita il numero di fonti processate per esecuzioni rapide.",
    )


def _add_generation_arguments(parser):
    parser.add_argument("--query", required=True, help="Nome area o alias da risolvere nel catalogo.")
    parser.add_argument("--catalog", default=str(AREA_CATALOG_DIR), help="Cartella catalogo aree.")
    parser.add_argument(
        "--project-template",
        default="project.yaml",
        help="Template project.yaml usato per generare la configurazione area-specifica.",
    )
    parser.add_argument(
        "--output-dir",
        default="generated",
        help="Cartella radice dove creare la configurazione generata.",
    )


def main():
    parser = build_parser()
    argv = _normalize_argv(sys.argv[1:])
    args = parser.parse_args(argv)

    if args.command == "list-areas":
        return handle_list_areas(args)
    if args.command == "resolve-area":
        return handle_resolve_area(args)
    if args.command == "generate-config":
        return handle_generate_config(args)
    if args.command == "bootstrap":
        return handle_bootstrap(args)
    if args.command == "analyze":
        return handle_analyze(args)
    return 1


def _normalize_argv(argv):
    known = {"analyze", "list-areas", "resolve-area", "generate-config", "bootstrap"}
    if not argv or argv[0].startswith("-") or argv[0] not in known:
        return ["analyze", *argv]
    return argv


def handle_list_areas(args):
    areas = load_area_catalog(_resolve_path(args.catalog))
    for area in areas:
        print(f"{area.slug}\t{area.name}\t{area.region}\t{len(area.source_seeds)} fonti seed")
    return 0


def handle_resolve_area(args):
    match = resolve_area(args.query, _resolve_path(args.catalog))
    payload = {
        "slug": match.area.slug,
        "name": match.area.name,
        "matched_on": match.matched_on,
        "score": match.score,
        "region": match.area.region,
        "province": match.area.province,
        "country": match.area.country,
        "radius_km": match.area.radius_km,
        "municipalities": match.area.municipalities,
        "source_seed_count": len(match.area.source_seeds),
    }
    if args.output:
        output_path = _resolve_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"[done] area salvata: {output_path}")
    else:
        print(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).strip())
    return 0


def handle_generate_config(args):
    paths = generate_area_configuration(args)
    print(f"[done] area: {paths.area_path}")
    print(f"[done] project: {paths.project_path}")
    print(f"[done] sources: {paths.sources_path}")
    print(f"[done] candidates: {paths.candidates_path}")
    return 0


def handle_bootstrap(args):
    paths = generate_area_configuration(args)
    print(f"[info] configurazione generata in: {paths.output_dir}")
    analyze_args = argparse.Namespace(
        command="analyze",
        provider=args.provider,
        project=paths.project_path,
        sources=paths.sources_path,
        candidates=paths.candidates_path,
        max_sources=args.max_sources,
    )
    return handle_analyze(analyze_args)


def generate_area_configuration(args):
    catalog_path = _resolve_path(args.catalog)
    match = resolve_area(args.query, catalog_path)
    template_path = _resolve_path(args.project_template)
    with template_path.open("r", encoding="utf-8") as handle:
        template_project = yaml.safe_load(handle) or {}

    generated_root = _resolve_path(args.output_dir)
    if generated_root == REPO_ROOT / "generated":
        output_dir = generated_root / match.area.slug
    else:
        output_dir = generated_root

    paths = create_generated_configs(match.area, template_project, output_dir)
    return paths


def handle_analyze(args):
    project_path = _resolve_path(args.project)
    sources_path = _resolve_path(args.sources)
    candidates_path = _resolve_path(args.candidates)

    project = load_project_config(project_path)
    sources = load_sources(sources_path)
    if args.max_sources is not None:
        sources = sources[: args.max_sources]

    provider = create_provider(args.provider)
    fetcher = Fetcher(project)
    analyzer = Analyzer(project, provider)

    raw_events = []
    discovered_sources = []
    fetch_failures = []

    print(f"[info] progetto: {project.name}")
    print(f"[info] fonti attive: {len(sources)}")
    if provider.name != "none":
        availability = "disponibile" if provider.is_available() else "non disponibile"
        print(f"[info] provider IA: {provider.name} ({availability})")
        if not provider.is_available() and provider.unavailable_reason:
            print(f"[warn] fallback euristico: {provider.unavailable_reason}")

    for index, source in enumerate(sources, start=1):
        print(f"[info] [{index}/{len(sources)}] analisi fonte: {source.name} -> {source.url}")
        try:
            document = fetcher.fetch(source)
        except Exception as exc:
            fetch_failures.append({"source": source.name, "url": source.url, "error": str(exc)})
            print(f"[warn] fetch fallito per {source.name}: {exc}")
            continue

        candidates = extract_candidate_events(document, project)
        suggestions = discover_candidate_sources(document, source)
        discovered_sources.extend(suggestions)

        print(f"[info] candidati trovati: {len(candidates)}")
        for candidate in candidates:
            candidate = enrich_candidate_from_detail(candidate, fetcher)
            event = analyzer.normalize_candidate(candidate)
            if event:
                raw_events.append(event)

    deduped_events = deduplicate_events(raw_events)
    working_dir = project_path.parent
    output_html = working_dir / project.output_html
    output_html.parent.mkdir(parents=True, exist_ok=True)
    html = render_events_html(project, deduped_events)
    output_html.write_text(html, encoding="utf-8")
    root_events_html = working_dir / "events.html"
    root_events_html.write_text(html, encoding="utf-8")

    output_json = output_html.with_suffix(".json")
    output_json.write_text(
        json.dumps([event.to_dict() for event in deduped_events], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    portal_exports = export_portal_payload(project, deduped_events, output_html.parent)

    merge_and_save_candidate_sources(candidates_path, discovered_sources)

    print(f"[done] eventi estratti: {len(raw_events)}")
    print(f"[done] eventi deduplicati: {len(deduped_events)}")
    print(f"[done] output HTML: {output_html}")
    print(f"[done] copia HTML: {root_events_html}")
    print(f"[done] output JSON: {output_json}")
    print(f"[done] export portale JSON: {portal_exports['portal_json']}")
    print(f"[done] export portale NDJSON: {portal_exports['portal_ndjson']}")
    print(f"[done] indice SEO: {portal_exports['seo_index']}")
    print(f"[done] indice ricerca: {portal_exports['search_index']}")
    print(f"[done] payload import sito: {portal_exports['site_import']}")
    if fetch_failures:
        print(f"[warn] fetch falliti: {len(fetch_failures)}")
    return 0


def _resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


if __name__ == "__main__":
    sys.exit(main())
