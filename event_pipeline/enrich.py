import re
from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from event_pipeline.models import CandidateEvent


YOUTUBE_HOSTS = ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com")
FLYER_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".webp")
FLYER_HINTS = ("flyer", "locandina", "manifesto", "programma", "brochure")


def enrich_candidate_from_detail(candidate: CandidateEvent, fetcher) -> CandidateEvent:
    if not _looks_like_html_url(candidate.source_url):
        return candidate

    try:
        document = fetcher.fetch_url(candidate.source_url, source=candidate.source)
    except Exception:
        return candidate

    if "html" not in (document.content_type or "").lower():
        return candidate

    soup = BeautifulSoup(document.html, "html.parser")
    detail_text = _extract_detail_text(soup)
    gallery_images = _extract_gallery_images(soup, document.final_url)
    flyer_urls = _extract_flyer_urls(soup, document.final_url)
    youtube_urls = _extract_youtube_urls(soup, document.final_url)

    if detail_text and len(detail_text) > len(candidate.detail_text or candidate.text or ""):
        candidate.detail_text = detail_text
    if not candidate.image_url and gallery_images:
        candidate.image_url = gallery_images[0]

    candidate.image_gallery = _merge_unique(candidate.image_gallery + gallery_images)
    candidate.flyer_urls = _merge_unique(candidate.flyer_urls + flyer_urls)
    candidate.youtube_urls = _merge_unique(candidate.youtube_urls + youtube_urls)
    return candidate


def _looks_like_html_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    parsed = urlparse(url)
    return not parsed.path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"))


def _extract_detail_text(soup: BeautifulSoup) -> str:
    meta_description = soup.find("meta", attrs={"name": "description"})
    og_description = soup.find("meta", attrs={"property": "og:description"})
    candidates = []
    for node in (meta_description, og_description):
        if node and node.get("content"):
            candidates.append(" ".join(node["content"].split()))

    content_roots = []
    for selector in ("article", "main", ".entry-content", ".post-content", ".tribe-events-single", ".mec-single-event-description"):
        content_roots.extend(soup.select(selector))

    if not content_roots:
        body = soup.body
        if body:
            content_roots.append(body)

    for root in content_roots[:4]:
        chunks = []
        for node in root.find_all(["p", "li"]):
            text = " ".join(node.get_text(" ", strip=True).split())
            if len(text) >= 35 and not _looks_like_junk_text(text):
                chunks.append(text)
        if chunks:
            candidates.append("\n\n".join(chunks[:12]))

    candidates = sorted(set(candidates), key=len, reverse=True)
    return candidates[0] if candidates else ""


def _extract_gallery_images(soup: BeautifulSoup, base_url: str) -> List[str]:
    urls = []
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        urls.append(urljoin(base_url, og_image["content"]))

    for image in soup.find_all("img", src=True):
        src = urljoin(base_url, image["src"])
        lowered = src.lower()
        if any(token in lowered for token in ("logo", "icon", "avatar", "banner-cookie")):
            continue
        urls.append(src)
        if len(urls) >= 12:
            break
    return _merge_unique(urls)


def _extract_flyer_urls(soup: BeautifulSoup, base_url: str) -> List[str]:
    urls = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        lowered_href = href.lower()
        label = " ".join(anchor.get_text(" ", strip=True).split()).lower()
        if lowered_href.endswith(FLYER_EXTENSIONS) or any(hint in label for hint in FLYER_HINTS):
            if any(lowered_href.endswith(ext) for ext in FLYER_EXTENSIONS):
                urls.append(href)
    return _merge_unique(urls[:8])


def _extract_youtube_urls(soup: BeautifulSoup, base_url: str) -> List[str]:
    urls = []
    for tag in soup.find_all(["a", "iframe"], href=True):
        href = urljoin(base_url, tag.get("href", ""))
        if _is_youtube_url(href):
            urls.append(href)
    for tag in soup.find_all("iframe", src=True):
        src = urljoin(base_url, tag["src"])
        if _is_youtube_url(src):
            urls.append(src)
    return _merge_unique(urls[:6])


def _is_youtube_url(url: str) -> bool:
    if not url:
        return False
    host = urlparse(url).netloc.lower()
    return host in YOUTUBE_HOSTS


def _looks_like_junk_text(text: str) -> bool:
    lowered = text.lower()
    junk_patterns = (
        "cookie",
        "privacy",
        "newsletter",
        "accedi",
        "registrati",
        "condividi",
        "leggi tutto",
    )
    return any(pattern in lowered for pattern in junk_patterns)


def _merge_unique(items: List[str]) -> List[str]:
    result = []
    seen = set()
    for item in items:
        clean = (item or "").strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result
