from pathlib import Path
from typing import Iterable, List

import yaml

from event_pipeline.models import ProjectConfig, SourceConfig


def _read_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File YAML non trovato: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_project_config(path: Path) -> ProjectConfig:
    data = _read_yaml(path)
    return ProjectConfig(
        name=data.get("name", "Event Source Analyzer"),
        description=data.get("description", ""),
        language=data.get("language", "it"),
        timezone=data.get("timezone", "Europe/Rome"),
        output_html=data.get("output_html", "output/events.html"),
        area_label=data.get("area_label", ""),
        theme=data.get("theme", "eventi"),
        known_municipalities=data.get("known_municipalities", []) or [],
        categories=data.get("categories", []) or [],
        include_keywords=data.get("include_keywords", []) or [],
        exclude_keywords=data.get("exclude_keywords", []) or [],
        event_link_keywords=data.get("event_link_keywords", []) or [],
        browser_timeout_seconds=int(data.get("browser_timeout_seconds", 18)),
        max_candidate_blocks_per_source=int(data.get("max_candidate_blocks_per_source", 40)),
    )


def load_sources(path: Path) -> List[SourceConfig]:
    data = _read_yaml(path)
    items = data.get("sources", []) or []
    defaults = data.get("defaults", {}) or {}
    social_policy = defaults.get("social_policy", {}) or {}
    result = []
    for item in items:
        enabled = item.get("active", item.get("enabled", defaults.get("enabled", True)))
        if not enabled:
            continue

        fetch_mode = str(item.get("fetch_mode", defaults.get("fetch_mode", "auto"))).lower()
        requires_browser = bool(item.get("requires_browser", False)) or fetch_mode == "browser"
        result.append(
            SourceConfig(
                name=item["name"],
                url=item["url"],
                type=item.get("type", "portale"),
                area=item.get("area", ""),
                priority=int(item.get("priority", 0)),
                source_id=item.get("id", ""),
                subtype=item.get("subtype", ""),
                municipality=item.get("municipality", "") or "",
                trust_level=item.get("trust_level", ""),
                parsing_profile=item.get("parsing_profile", "auto"),
                note=item.get("note", item.get("notes", "")),
                requires_browser=requires_browser,
                discovery_only=bool(item.get("discovery_only", social_policy.get("discovery_only", False))),
            )
        )
    result.sort(key=lambda source: source.priority, reverse=True)
    return result


def _normalize_candidate_source(item):
    return {
        "id": item.get("id", "").strip(),
        "name": item.get("name", "").strip(),
        "url": item.get("url", "").strip(),
        "type": item.get("type", "portale").strip(),
        "subtype": item.get("subtype", "").strip(),
        "area": item.get("area", "").strip(),
        "municipality": item.get("municipality", ""),
        "categories_hint": item.get("categories_hint", []) or [],
        "priority": int(item.get("priority", 1)),
        "trust_level": item.get("trust_level", ""),
        "parsing_profile": item.get("parsing_profile", "auto"),
        "discovery_only": bool(item.get("discovery_only", item.get("type", "") == "social")),
        "notes": item.get("notes", item.get("note", "")).strip(),
    }


def merge_and_save_candidate_sources(path: Path, candidates: Iterable[dict]):
    existing = _read_yaml(path) if path.exists() else {}
    current_items = existing.get("sources_candidates", []) or []

    indexed = {}
    for item in current_items:
        normalized = _normalize_candidate_source(item)
        if normalized["url"]:
            indexed[normalized["url"]] = normalized

    for item in candidates:
        normalized = _normalize_candidate_source(item)
        if normalized["url"] and normalized["url"] not in indexed:
            indexed[normalized["url"]] = normalized

    payload = {
        "version": existing.get("version", 1),
        "project": existing.get("project", "generic-events"),
        "sources_candidates": list(indexed.values()),
    }
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
