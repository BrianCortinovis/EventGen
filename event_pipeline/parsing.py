import json
import re
from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from event_pipeline.models import CandidateEvent, FetchedDocument, ProjectConfig, SourceConfig


EVENT_CLASS_HINTS = (
    "event",
    "evento",
    "events",
    "manifest",
    "calendar",
    "tribe",
    "mec",
    "spettac",
    "festival",
)


def extract_candidate_events(document: FetchedDocument, project: ProjectConfig) -> List[CandidateEvent]:
    soup = BeautifulSoup(document.html, "html.parser")
    candidates = []
    candidates.extend(_extract_jsonld_events(soup, document))
    candidates.extend(_extract_block_events(soup, document, project))
    return _dedupe_candidates(candidates)


def discover_candidate_sources(document: FetchedDocument, source: SourceConfig) -> List[dict]:
    soup = BeautifulSoup(document.html, "html.parser")
    source_domain = urlparse(source.url).netloc.lower()
    suggestions = []
    seen = set()

    for anchor in soup.find_all("a", href=True):
        href = urljoin(document.final_url, anchor["href"])
        parsed = urlparse(href)
        if not parsed.scheme.startswith("http"):
            continue
        if parsed.netloc.lower() == source_domain:
            continue
        url = href.split("#", 1)[0]
        anchor_text = " ".join(anchor.get_text(" ", strip=True).split()).lower()
        url_text = url.lower()
        candidate_type = None

        if "facebook.com" in url_text or "instagram.com" in url_text:
            candidate_type = "social"
        elif any(token in anchor_text or token in url_text for token in ("event", "eventi", "manifest", "proloco", "museo", "teatro", "turismo", "comune")):
            candidate_type = "portale"

        if not candidate_type or url in seen:
            continue

        seen.add(url)
        suggestions.append(
            {
                "id": "",
                "name": anchor.get_text(" ", strip=True)[:120] or parsed.netloc,
                "url": url,
                "type": candidate_type,
                "subtype": "",
                "area": source.area,
                "municipality": "",
                "categories_hint": [],
                "priority": 1,
                "trust_level": "low" if candidate_type == "social" else "medium",
                "parsing_profile": "social" if candidate_type == "social" else "auto",
                "discovery_only": candidate_type == "social",
                "notes": f"Scoperta automaticamente da {source.name}; verificare e attivare manualmente.",
            }
        )

        if len(suggestions) >= 12:
            break

    return suggestions


def _extract_jsonld_events(soup: BeautifulSoup, document: FetchedDocument) -> List[CandidateEvent]:
    candidates = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (script.string or script.get_text() or "").strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue

        for node in _flatten_jsonld(payload):
            kind = str(node.get("@type", "")).lower()
            if "event" not in kind:
                continue
            location = node.get("location") or {}
            address = location.get("address") if isinstance(location, dict) else {}
            raw_location = ""
            if isinstance(location, dict):
                raw_location = " - ".join(
                    part
                    for part in [
                        location.get("name", ""),
                        address.get("addressLocality", "") if isinstance(address, dict) else "",
                    ]
                    if part
                )
            candidates.append(
                CandidateEvent(
                    source=document.source,
                    title=(node.get("name") or "").strip(),
                    text=_jsonld_description(node),
                    source_url=node.get("url") or document.final_url,
                    raw_date=node.get("startDate", "") or "",
                    raw_end_date=node.get("endDate", "") or "",
                    raw_time="",
                    raw_location=raw_location,
                    image_url=_jsonld_image(node),
                    image_gallery=[url for url in [_jsonld_image(node)] if url],
                    organizer=_extract_name(node.get("organizer")),
                    tags=[],
                    discovery_only=document.source.discovery_only,
                    metadata={"extraction": "jsonld"},
                )
            )
    return [item for item in candidates if item.title]


def _extract_block_events(soup: BeautifulSoup, document: FetchedDocument, project: ProjectConfig) -> List[CandidateEvent]:
    results = []
    max_blocks = project.max_candidate_blocks_per_source
    seen_fingerprints = set()

    for element in soup.find_all(["article", "section", "div", "li"]):
        text = " ".join(element.get_text(" ", strip=True).split())
        if len(text) < 40 or len(text) > 4000:
            continue

        attrs_blob = " ".join(
            [
                " ".join(element.get("class", [])),
                element.get("id", ""),
                element.name,
            ]
        ).lower()
        has_hint = any(hint in attrs_blob for hint in EVENT_CLASS_HINTS)
        has_date = bool(_find_date_like_text(text))
        has_event_word = any(token in text.lower() for token in ("evento", "eventi", "manifestazione", "sagra", "concerto", "mostra", "mercatino", "festival"))

        if not (has_hint or has_date or has_event_word):
            continue

        title = _extract_title(element)
        if not title or len(title) < 4:
            continue

        fingerprint = f"{title.lower()}::{text[:120].lower()}"
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)

        link = _extract_link(element, document.final_url)
        image_url = _extract_image(element, document.final_url)
        image_gallery = _extract_images(element, document.final_url)
        time_tag = element.find("time")
        raw_date = ""
        if time_tag:
            raw_date = time_tag.get("datetime", "") or time_tag.get_text(" ", strip=True)
        if not raw_date:
            raw_date = _find_date_like_text(text)

        results.append(
            CandidateEvent(
                source=document.source,
                title=title,
                text=text,
                source_url=link or document.final_url,
                raw_date=raw_date,
                raw_end_date="",
                raw_time=_find_time_like_text(text),
                raw_location=_find_location_like_text(text),
                image_url=image_url,
                image_gallery=image_gallery,
                organizer="",
                tags=[],
                discovery_only=document.source.discovery_only,
                metadata={"extraction": "html-block"},
            )
        )

        if len(results) >= max_blocks:
            break

    return results


def _flatten_jsonld(payload):
    if isinstance(payload, list):
        for item in payload:
            yield from _flatten_jsonld(item)
        return
    if isinstance(payload, dict):
        yield payload
        for key in ("@graph", "itemListElement"):
            value = payload.get(key)
            if value:
                yield from _flatten_jsonld(value)


def _extract_name(value):
    if isinstance(value, dict):
        return value.get("name", "")
    if isinstance(value, str):
        return value
    return ""


def _jsonld_image(node):
    image = node.get("image")
    if isinstance(image, list) and image:
        return image[0]
    if isinstance(image, str):
        return image
    return ""


def _jsonld_description(node):
    pieces = [
        node.get("description", ""),
        _extract_name(node.get("location")),
    ]
    return " ".join(part.strip() for part in pieces if isinstance(part, str) and part.strip())


def _extract_title(element):
    for tag in ("h1", "h2", "h3", "h4", "strong"):
        match = element.find(tag)
        if match:
            text = " ".join(match.get_text(" ", strip=True).split())
            if text:
                return text
    anchor = element.find("a")
    if anchor:
        return " ".join(anchor.get_text(" ", strip=True).split())
    return ""


def _extract_link(element, base_url):
    anchor = element.find("a", href=True)
    if not anchor:
        return ""
    return urljoin(base_url, anchor["href"])


def _extract_image(element, base_url):
    image = element.find("img", src=True)
    if not image:
        return ""
    return urljoin(base_url, image["src"])


def _extract_images(element, base_url):
    urls = []
    for image in element.find_all("img", src=True):
        urls.append(urljoin(base_url, image["src"]))
        if len(urls) >= 4:
            break
    return urls


def _find_date_like_text(text):
    patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",
        r"\b\d{1,2}\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}\b",
        r"\bdal\s+\d{1,2}\s+al\s+\d{1,2}\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4}\b",
    ]
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def _find_time_like_text(text):
    match = re.search(r"\b(?:ore\s*)?(\d{1,2}[:.]\d{2})\b", text.lower())
    if match:
        return match.group(1).replace(".", ":")
    return ""


def _find_location_like_text(text):
    patterns = [
        r"(?:presso|luogo|location|ritrovo|partenza|in)\s+([A-ZÀ-Ý][^.;,:]{3,80})",
        r"(?:piazza|parco|teatro|museo|centro|palazzetto|campo)\s+([A-ZÀ-Ý][^.;,:]{2,80})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())
    return ""


def _dedupe_candidates(candidates: List[CandidateEvent]) -> List[CandidateEvent]:
    seen = set()
    unique = []
    for item in candidates:
        key = (item.title.strip().lower(), item.source_url.strip().lower(), item.raw_date.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
