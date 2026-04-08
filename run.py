#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from event_pipeline.analysis import Analyzer
from event_pipeline.config import (
    load_project_config,
    load_sources,
    merge_and_save_candidate_sources,
)
from event_pipeline.dedupe import deduplicate_events
from event_pipeline.fetch import Fetcher
from event_pipeline.parsing import discover_candidate_sources, extract_candidate_events
from event_pipeline.providers import create_provider
from event_pipeline.render_html import render_events_html


def build_parser():
    parser = argparse.ArgumentParser(
        description="Pipeline manuale per raccogliere e strutturare eventi da fonti web e social."
    )
    parser.add_argument(
        "--provider",
        default="none",
        choices=["none", "openai", "claude", "gemini"],
        help="Provider IA opzionale per analisi e classificazione.",
    )
    parser.add_argument(
        "--project",
        default="project.yaml",
        help="Percorso del file project.yaml",
    )
    parser.add_argument(
        "--sources",
        default="sources.yaml",
        help="Percorso del file sources.yaml",
    )
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
    return parser


def main():
    args = build_parser().parse_args()
    root = Path(__file__).resolve().parent

    project = load_project_config(root / args.project)
    sources = load_sources(root / args.sources)
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
            event = analyzer.normalize_candidate(candidate)
            if event:
                raw_events.append(event)

    deduped_events = deduplicate_events(raw_events)
    output_html = root / project.output_html
    output_html.parent.mkdir(parents=True, exist_ok=True)
    html = render_events_html(project, deduped_events)
    output_html.write_text(html, encoding="utf-8")
    root_events_html = root / "events.html"
    root_events_html.write_text(html, encoding="utf-8")

    output_json = output_html.with_suffix(".json")
    output_json.write_text(
        json.dumps([event.to_dict() for event in deduped_events], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    merge_and_save_candidate_sources(root / args.candidates, discovered_sources)

    print(f"[done] eventi estratti: {len(raw_events)}")
    print(f"[done] eventi deduplicati: {len(deduped_events)}")
    print(f"[done] output HTML: {output_html}")
    print(f"[done] copia HTML: {root_events_html}")
    print(f"[done] output JSON: {output_json}")
    if fetch_failures:
        print(f"[warn] fetch falliti: {len(fetch_failures)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
