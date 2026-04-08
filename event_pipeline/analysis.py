import json
import re
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional, Tuple

from event_pipeline.models import CandidateEvent, EventRecord, ProjectConfig


MONTHS = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


CATEGORY_KEYWORDS = {
    "Mostre": ("mostra", "mostre", "esposizione", "vernissage", "galleria"),
    "Cinema": ("cinema", "film", "proiezione", "rassegna cinematografica"),
    "Musica e spettacoli": ("concerto", "musica", "spettacolo", "teatro", "live", "festival"),
    "Famiglia": ("bambini", "famiglia", "laboratorio", "kids", "animazione"),
    "Sagre e feste": ("sagra", "festa", "festa patronale", "polenta", "street food"),
    "Mercatini": ("mercatino", "mercatini", "bancarelle", "artigianato", "antiquariato"),
    "Sport": ("gara", "corsa", "torneo", "sport", "trail", "camminata", "bike"),
    "Outdoor": ("escursione", "trekking", "nordic walking", "outdoor", "alpin", "mountain"),
    "Tradizioni": ("tradizione", "folklore", "storica", "rievocazione", "sfilata"),
    "Cultura": ("cultura", "incontro", "presentazione", "conferenza", "libro", "museo"),
}


class Analyzer:
    def __init__(self, project: ProjectConfig, provider):
        self.project = project
        self.provider = provider

    def normalize_candidate(self, candidate: CandidateEvent) -> Optional[EventRecord]:
        merged_text = " ".join(part for part in [candidate.title, candidate.text, candidate.raw_location] if part).strip()

        if self._contains_excluded_text(merged_text):
            return None
        if self._is_generic_listing_title(candidate.title):
            return None

        ai_data = {}
        if self.provider.is_available():
            ai_data = self.provider.extract_event(candidate, self.project) or {}

        start_date, end_date = self._resolve_dates(candidate, ai_data)
        if not start_date:
            return None

        if not self._looks_like_public_event(candidate, merged_text, ai_data):
            return None

        municipality = self._guess_municipality(candidate, merged_text, ai_data)
        venue = self._guess_venue(candidate, ai_data)
        category, subcategory = self._classify_category(candidate, merged_text, ai_data)
        organizer = self._guess_organizer(candidate, ai_data)
        full_description = self._build_full_description(candidate, ai_data)
        description = self._build_short_description(full_description, ai_data)
        reliability, confirmation_status = self._compute_reliability(candidate)
        event_id = self._build_id(candidate.title, start_date, municipality)

        return EventRecord(
            id=event_id,
            title=self._clean_text(ai_data.get("title") or candidate.title),
            short_description=description,
            full_description=full_description,
            start_date=start_date,
            end_date=end_date,
            time_text=self._clean_text(ai_data.get("time") or candidate.raw_time),
            municipality=municipality,
            venue=venue,
            category=category,
            subcategory=subcategory,
            organizer=organizer,
            source=candidate.source.name,
            source_url=candidate.source_url,
            image_url=ai_data.get("image_url") or candidate.image_url,
            gallery_images=self._merge_urls(candidate.image_gallery, [candidate.image_url]),
            flyer_urls=self._merge_urls(candidate.flyer_urls),
            youtube_urls=self._merge_urls(candidate.youtube_urls),
            tags=sorted(set(candidate.tags + self._extract_tags(candidate, category))),
            reliability=reliability,
            confirmation_status=confirmation_status,
            secondary_sources=[],
        )

    def _resolve_dates(self, candidate: CandidateEvent, ai_data: dict) -> Tuple[str, str]:
        if ai_data.get("start_date"):
            return ai_data.get("start_date", ""), ai_data.get("end_date", "")

        for raw in [candidate.raw_date, candidate.text]:
            start_date, end_date = parse_date_range(raw)
            if start_date:
                return start_date, end_date
        return "", ""

    def _looks_like_public_event(self, candidate: CandidateEvent, merged_text: str, ai_data: dict) -> bool:
        if ai_data.get("is_event") is False:
            return False

        lowered = merged_text.lower()
        include_hits = sum(1 for token in self.project.include_keywords if token.lower() in lowered)
        if include_hits:
            return True

        category, _ = self._classify_category(candidate, merged_text, ai_data)
        return bool(category)

    def _contains_excluded_text(self, text: str) -> bool:
        lowered = text.lower()
        return any(token.lower() in lowered for token in self.project.exclude_keywords)

    def _is_generic_listing_title(self, title: str) -> bool:
        lowered = self._clean_text(title).lower()
        generic_patterns = (
            "i prossimi eventi",
            "prossimi eventi",
            "calendario eventi",
            "tutti gli eventi",
            "eventi in ",
            "eventi",
        )
        return any(lowered == pattern or lowered.startswith(pattern) for pattern in generic_patterns)

    def _guess_municipality(self, candidate: CandidateEvent, text: str, ai_data: dict) -> str:
        if ai_data.get("municipality"):
            return self._clean_text(ai_data["municipality"])

        lowered = text.lower()
        for municipality in self.project.known_municipalities:
            if municipality.lower() in lowered:
                return municipality

        location = candidate.raw_location.strip()
        if location and candidate.source.area and candidate.source.area.lower() != location.lower():
            return candidate.source.area
        return candidate.source.area

    def _guess_venue(self, candidate: CandidateEvent, ai_data: dict) -> str:
        if ai_data.get("venue"):
            return self._clean_text(ai_data["venue"])
        return self._clean_text(candidate.raw_location)

    def _classify_category(self, candidate: CandidateEvent, text: str, ai_data: dict) -> Tuple[str, str]:
        if ai_data.get("category"):
            return self._clean_text(ai_data["category"]), self._clean_text(ai_data.get("subcategory", ""))

        lowered = " ".join([candidate.title, text]).lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return category, ""
        return "Cultura", ""

    def _guess_organizer(self, candidate: CandidateEvent, ai_data: dict) -> str:
        if ai_data.get("organizer"):
            return self._clean_text(ai_data["organizer"])
        if candidate.organizer:
            return self._clean_text(candidate.organizer)
        return candidate.source.name

    def _build_full_description(self, candidate: CandidateEvent, ai_data: dict) -> str:
        text = self._clean_text(ai_data.get("full_description") or candidate.detail_text or candidate.text)
        return text

    def _build_short_description(self, full_description: str, ai_data: dict) -> str:
        text = self._clean_text(ai_data.get("short_description") or full_description)
        if len(text) <= 220:
            return text
        shortened = text[:217].rsplit(" ", 1)[0].strip()
        return f"{shortened}..."

    def _compute_reliability(self, candidate: CandidateEvent) -> Tuple[str, str]:
        kind = candidate.source.type.lower()
        trust_level = candidate.source.trust_level.lower()
        if trust_level in {"high", "alta"}:
            reliability = "alta"
        elif trust_level in {"medium", "media"}:
            reliability = "media"
        elif trust_level in {"low", "bassa"}:
            reliability = "bassa"
        elif kind in {"comune", "proloco", "museo", "institution", "museum"}:
            reliability = "alta"
        elif kind in {"portale", "aggregatore", "portal", "aggregator", "local_portal", "cultural_portal"}:
            reliability = "media"
        else:
            reliability = "media"

        if kind == "social" or candidate.discovery_only:
            return "bassa", "non confermato"
        return reliability, "confermato"

    def _extract_tags(self, candidate: CandidateEvent, category: str):
        tags = [category.lower()]
        if candidate.source.discovery_only:
            tags.append("social-discovery")
        return tags

    def _build_id(self, title: str, start_date: str, municipality: str) -> str:
        raw = f"{title}-{start_date}-{municipality}".strip("-")
        slug = slugify(raw)
        return slug or "event"

    def _clean_text(self, value: str) -> str:
        return " ".join((value or "").split()).strip()

    def _merge_urls(self, primary_items, extra_items=None):
        items = list(primary_items or [])
        items.extend(extra_items or [])
        merged = []
        seen = set()
        for item in items:
            clean = (item or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            merged.append(clean)
        return merged


def parse_date_range(text: str) -> Tuple[str, str]:
    text = (text or "").strip()
    if not text:
        return "", ""

    compact = " ".join(text.replace("–", "-").split()).lower()

    range_match = re.search(
        r"\bdal\s+(\d{1,2})\s+al\s+(\d{1,2})\s+([a-zà-ù]+)\s+(\d{4})\b",
        compact,
        flags=re.IGNORECASE,
    )
    if range_match:
        day_start, day_end, month_name, year = range_match.groups()
        month = MONTHS.get(strip_accents(month_name))
        if month:
            return _iso_date(int(year), month, int(day_start)), _iso_date(int(year), month, int(day_end))

    full_date = re.search(
        r"\b(\d{1,2})\s+([a-zà-ù]+)\s+(\d{4})\b",
        compact,
        flags=re.IGNORECASE,
    )
    if full_date:
        day, month_name, year = full_date.groups()
        month = MONTHS.get(strip_accents(month_name))
        if month:
            return _iso_date(int(year), month, int(day)), ""

    numeric = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", compact)
    if numeric:
        day, month, year = numeric.groups()
        year = int(year)
        if year < 100:
            year += 2000
        return _iso_date(year, int(month), int(day)), ""

    return "", ""


def slugify(value: str) -> str:
    value = strip_accents(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(a=a.lower(), b=b.lower()).ratio()


def _iso_date(year: int, month: int, day: int) -> str:
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return ""
