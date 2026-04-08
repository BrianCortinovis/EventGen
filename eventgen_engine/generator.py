from pathlib import Path
from typing import Dict

import yaml

from eventgen_engine.models import AreaDefinition, GeneratedConfigPaths


DEFAULT_CONFIDENCE_POLICY = {
    "official": "high",
    "aggregator": "medium",
    "social": "low",
}

DEFAULT_SOCIAL_POLICY = {
    "discovery_only": True,
    "requires_confirmation": True,
}


def create_generated_configs(area: AreaDefinition, template_project: dict, output_dir: Path) -> GeneratedConfigPaths:
    output_dir.mkdir(parents=True, exist_ok=True)

    area_payload = build_area_payload(area)
    project_payload = build_project_payload(template_project, area)
    sources_payload = build_sources_payload(area)
    candidates_payload = build_candidates_payload(area)

    area_path = output_dir / "area.yaml"
    project_path = output_dir / "project.yaml"
    sources_path = output_dir / "sources.yaml"
    candidates_path = output_dir / "sources_candidates.yaml"

    _write_yaml(area_path, area_payload)
    _write_yaml(project_path, project_payload)
    _write_yaml(sources_path, sources_payload)
    _write_yaml(candidates_path, candidates_payload)

    return GeneratedConfigPaths(
        area_path=str(area_path),
        project_path=str(project_path),
        sources_path=str(sources_path),
        candidates_path=str(candidates_path),
        output_dir=str(output_dir),
    )


def build_area_payload(area: AreaDefinition) -> dict:
    return {
        "slug": area.slug,
        "name": area.name,
        "aliases": area.aliases,
        "area_type": area.area_type,
        "region": area.region,
        "province": area.province,
        "country": area.country,
        "center": {
            "latitude": area.center_latitude,
            "longitude": area.center_longitude,
        },
        "radius_km": area.radius_km,
        "municipalities": area.municipalities,
        "search_labels": area.search_labels,
        "notes": area.notes,
    }


def build_project_payload(template_project: dict, area: AreaDefinition) -> dict:
    payload = dict(template_project)
    payload["name"] = f"EventGEn - {area.name}"
    payload["description"] = (
        f"Configurazione generata per {area.name}. "
        "Motore locale per generare fonti compatibili e analizzare eventi pubblici."
    )
    payload["area_label"] = area.name
    payload["theme"] = "eventi pubblici territoriali"
    payload["known_municipalities"] = area.municipalities
    payload["output_html"] = "output/events.html"
    return payload


def build_sources_payload(area: AreaDefinition) -> dict:
    return {
        "version": 1,
        "project": area.slug,
        "region": area.region,
        "country": area.country,
        "notes": (
            f"Fonti iniziali generate per {area.name}. "
            "Questa base puo essere estesa dalla futura UX desktop di EventGEn."
        ),
        "defaults": {
            "enabled": True,
            "fetch_mode": "auto",
            "output_language": "it",
            "confidence_policy": DEFAULT_CONFIDENCE_POLICY,
            "social_policy": DEFAULT_SOCIAL_POLICY,
        },
        "sources": area.source_seeds,
    }


def build_candidates_payload(area: AreaDefinition) -> dict:
    return {
        "version": 1,
        "project": area.slug,
        "sources_candidates": [],
    }


def _write_yaml(path: Path, payload: Dict):
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
