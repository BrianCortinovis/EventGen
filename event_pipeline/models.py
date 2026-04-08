from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectConfig:
    name: str
    description: str
    language: str
    timezone: str
    output_html: str
    area_label: str
    theme: str
    known_municipalities: List[str]
    categories: List[str]
    include_keywords: List[str]
    exclude_keywords: List[str]
    event_link_keywords: List[str]
    browser_timeout_seconds: int = 18
    max_candidate_blocks_per_source: int = 40


@dataclass
class SourceConfig:
    name: str
    url: str
    type: str
    area: str
    priority: int
    source_id: str = ""
    subtype: str = ""
    municipality: str = ""
    trust_level: str = ""
    parsing_profile: str = "auto"
    note: str = ""
    requires_browser: bool = False
    discovery_only: bool = False


@dataclass
class FetchedDocument:
    source: SourceConfig
    url: str
    final_url: str
    html: str
    content_type: str
    status_code: int


@dataclass
class CandidateEvent:
    source: SourceConfig
    title: str
    text: str
    source_url: str
    raw_date: str = ""
    raw_end_date: str = ""
    raw_time: str = ""
    raw_location: str = ""
    image_url: str = ""
    detail_text: str = ""
    image_gallery: List[str] = field(default_factory=list)
    flyer_urls: List[str] = field(default_factory=list)
    youtube_urls: List[str] = field(default_factory=list)
    organizer: str = ""
    tags: List[str] = field(default_factory=list)
    discovery_only: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventRecord:
    id: str
    title: str
    short_description: str
    full_description: str
    start_date: str
    end_date: str
    time_text: str
    municipality: str
    venue: str
    category: str
    subcategory: str
    organizer: str
    source: str
    source_url: str
    image_url: str
    gallery_images: List[str]
    flyer_urls: List[str]
    youtube_urls: List[str]
    tags: List[str]
    reliability: str
    confirmation_status: str
    secondary_sources: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
