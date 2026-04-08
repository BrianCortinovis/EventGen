from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AreaDefinition:
    slug: str
    name: str
    aliases: List[str]
    area_type: str
    region: str
    province: str
    country: str
    center_latitude: Optional[float]
    center_longitude: Optional[float]
    radius_km: Optional[int]
    municipalities: List[str]
    search_labels: List[str]
    notes: str
    source_seeds: List[Dict]


@dataclass
class GeneratedConfigPaths:
    area_path: str
    project_path: str
    sources_path: str
    candidates_path: str
    output_dir: str


@dataclass
class AreaMatch:
    area: AreaDefinition
    score: int
    matched_on: str = ""
