from pathlib import Path
from typing import List

import yaml

from eventgen_engine.models import AreaDefinition, AreaMatch


def load_area_catalog(directory: Path) -> List[AreaDefinition]:
    areas = []
    for path in sorted(directory.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        areas.append(_build_area_definition(data))
    return areas


def resolve_area(query: str, directory: Path) -> AreaMatch:
    normalized_query = _normalize(query)
    matches = []
    for area in load_area_catalog(directory):
        score, matched_on = _score_area_match(normalized_query, area)
        if score > 0:
            matches.append(AreaMatch(area=area, score=score, matched_on=matched_on))

    if not matches:
        available = ", ".join(area.name for area in load_area_catalog(directory))
        raise ValueError(f"Nessuna area trovata per '{query}'. Aree disponibili: {available}")

    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[0]


def _build_area_definition(data: dict) -> AreaDefinition:
    center = data.get("center", {}) or {}
    return AreaDefinition(
        slug=data["slug"],
        name=data["name"],
        aliases=data.get("aliases", []) or [],
        area_type=data.get("area_type", "custom"),
        region=data.get("region", ""),
        province=data.get("province", ""),
        country=data.get("country", "IT"),
        center_latitude=center.get("latitude"),
        center_longitude=center.get("longitude"),
        radius_km=data.get("radius_km"),
        municipalities=data.get("municipalities", []) or [],
        search_labels=data.get("search_labels", []) or [],
        notes=data.get("notes", ""),
        source_seeds=data.get("source_seeds", []) or [],
    )


def _score_area_match(query: str, area: AreaDefinition):
    candidates = [area.slug, area.name, *area.aliases, *area.search_labels]
    best_score = 0
    best_label = ""
    for candidate in candidates:
        normalized = _normalize(candidate)
        if not normalized:
            continue
        if query == normalized:
            return 100, candidate
        if query in normalized or normalized in query:
            score = 80
        elif all(part in normalized for part in query.split()):
            score = 65
        else:
            score = 0
        if score > best_score:
            best_score = score
            best_label = candidate
    return best_score, best_label


def _normalize(value: str) -> str:
    return " ".join((value or "").strip().lower().replace("-", " ").split())
