import json
from pathlib import Path

from event_pipeline.analysis import slugify


def export_portal_payload(project, events, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [build_portal_record(project, event) for event in events]

    portal_json_path = output_dir / "portal_events.json"
    portal_ndjson_path = output_dir / "portal_events.ndjson"
    seo_index_path = output_dir / "seo_index.json"
    search_index_path = output_dir / "search_index.ndjson"
    site_import_path = output_dir / "site_import.json"

    portal_json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    portal_ndjson_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records),
        encoding="utf-8",
    )
    seo_index_path.write_text(
        json.dumps(
            [
                {
                    "id": record["id"],
                    "slug": record["slug"],
                    "title": record["title"],
                    "seo_title": record["seo"]["title"],
                    "seo_description": record["seo"]["description"],
                    "keywords": record["seo"]["keywords"],
                    "canonical_path": record["seo"]["canonical_path"],
                    "robots": record["seo"]["robots"],
                    "primary_keyword": record["seo"]["primary_keyword"],
                    "open_graph": record["seo"]["open_graph"],
                    "twitter": record["seo"]["twitter"],
                }
                for record in records
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    search_index_path.write_text(
        "\n".join(
            json.dumps(
                {
                    "id": record["id"],
                    "slug": record["slug"],
                    "title": record["title"],
                    "municipality": record["event"]["municipality"],
                    "category": record["event"]["category"],
                    "tags": record["event"]["tags"],
                    "analytics_labels": record["analytics"]["labels"],
                    "text": record["search"]["document"],
                },
                ensure_ascii=False,
            )
            for record in records
        ),
        encoding="utf-8",
    )
    site_import_path.write_text(
        json.dumps(
            {
                "project": {
                    "name": project.name,
                    "language": project.language,
                    "area_label": project.area_label,
                    "theme": project.theme,
                },
                "generated_items": len(records),
                "items": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "portal_json": str(portal_json_path),
        "portal_ndjson": str(portal_ndjson_path),
        "seo_index": str(seo_index_path),
        "search_index": str(search_index_path),
        "site_import": str(site_import_path),
    }


def build_portal_record(project, event):
    slug = slugify(f"{event.title}-{event.start_date}-{event.municipality}") or event.id
    seo_keywords = _build_keywords(project, event)
    location_label = _build_location_label(event)
    primary_keyword = _pick_primary_keyword(event, project, seo_keywords)
    media_assets = []

    if event.image_url:
        media_assets.append({"kind": "hero_image", "url": event.image_url})
    media_assets.extend({"kind": "gallery_image", "url": url} for url in event.gallery_images if url != event.image_url)
    media_assets.extend({"kind": "flyer", "url": url} for url in event.flyer_urls)
    media_assets.extend({"kind": "youtube", "url": url} for url in event.youtube_urls)

    return {
        "id": event.id,
        "slug": slug,
        "title": event.title,
        "excerpt": event.short_description,
        "body": event.full_description,
        "summary": event.short_description,
        "event": {
            "start_date": event.start_date,
            "end_date": event.end_date,
            "time": event.time_text,
            "municipality": event.municipality,
            "venue": event.venue,
            "location_label": location_label,
            "organizer": event.organizer,
            "category": event.category,
            "subcategory": event.subcategory,
            "tags": event.tags,
            "reliability": event.reliability,
            "confirmation_status": event.confirmation_status,
        },
        "media": {
            "hero_image": event.image_url,
            "gallery": event.gallery_images,
            "flyers": event.flyer_urls,
            "youtube_links": event.youtube_urls,
            "assets": media_assets,
        },
        "source": {
            "primary_name": event.source,
            "primary_url": event.source_url,
            "secondary_sources": event.secondary_sources,
        },
        "seo": {
            "title": _build_seo_title(event),
            "description": _build_seo_description(event),
            "keywords": seo_keywords,
            "primary_keyword": primary_keyword,
            "canonical_path": f"/eventi/{slug}",
            "og_image": event.image_url,
            "robots": "index,follow",
            "open_graph": {
                "type": "article",
                "title": _build_seo_title(event),
                "description": _build_seo_description(event),
                "url": f"/eventi/{slug}",
                "image": event.image_url,
                "site_name": project.name,
                "locale": project.language,
            },
            "twitter": {
                "card": "summary_large_image" if event.image_url else "summary",
                "title": _build_seo_title(event),
                "description": _build_seo_description(event),
                "image": event.image_url,
            },
        },
        "search": {
            "document": _build_search_document(project, event),
            "boost": _build_search_boost(event),
        },
        "analytics": {
            "content_group": "events",
            "content_type": "event",
            "labels": _build_analytics_labels(project, event, slug),
            "dimensions": {
                "event_id": event.id,
                "event_slug": slug,
                "event_title": event.title,
                "event_category": event.category,
                "event_subcategory": event.subcategory,
                "event_municipality": event.municipality,
                "event_source": event.source,
                "event_reliability": event.reliability,
                "event_confirmation_status": event.confirmation_status,
                "event_start_date": event.start_date,
                "event_end_date": event.end_date,
                "has_image": bool(event.image_url),
                "has_gallery": bool(event.gallery_images),
                "has_flyer": bool(event.flyer_urls),
                "has_youtube": bool(event.youtube_urls),
                "area_label": project.area_label,
                "theme": project.theme,
            },
            "ga4_recommended_events": {
                "select_item": {
                    "item_id": event.id,
                    "item_name": event.title,
                    "item_category": event.category,
                    "item_category2": event.subcategory,
                    "item_variant": event.municipality,
                    "item_list_name": project.area_label,
                },
                "view_item": {
                    "item_id": event.id,
                    "item_name": event.title,
                    "item_category": event.category,
                    "item_category2": event.subcategory,
                    "item_variant": event.municipality,
                },
            },
        },
        "schema_org": {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": event.title,
            "description": event.short_description or event.full_description,
            "startDate": event.start_date,
            "endDate": event.end_date or event.start_date,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
                "@type": "Place",
                "name": event.venue or event.municipality or project.area_label,
                "address": location_label or project.area_label,
            },
            "image": [url for url in [event.image_url, *event.gallery_images] if url],
            "organizer": {
                "@type": "Organization",
                "name": event.organizer or event.source,
            },
            "performer": {
                "@type": "Organization",
                "name": event.organizer or event.source,
            },
            "keywords": ", ".join(seo_keywords),
        },
        "publishing": {
            "status": "ready",
            "content_type": "event",
            "language": project.language,
            "area_label": project.area_label,
            "theme": project.theme,
        },
        "cms": {
            "collection": "events",
            "entry_status": "draft",
            "path": f"/eventi/{slug}",
            "headline": event.title,
            "dek": event.short_description,
            "body_markdown": _build_body_markdown(event),
        },
    }


def _build_keywords(project, event):
    raw = [
        event.category,
        event.subcategory,
        event.municipality,
        event.venue,
        project.area_label,
        *event.tags,
    ]
    result = []
    seen = set()
    for item in raw:
        clean = " ".join((item or "").split()).strip()
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(clean)
    return result


def _pick_primary_keyword(event, project, keywords):
    for candidate in (
        event.title,
        event.category,
        event.municipality,
        project.area_label,
        keywords[0] if keywords else "",
    ):
        clean = " ".join((candidate or "").split()).strip()
        if clean:
            return clean
    return ""


def _build_seo_title(event):
    chunks = [event.title]
    if event.municipality:
        chunks.append(event.municipality)
    if event.start_date:
        chunks.append(event.start_date)
    return " | ".join(chunks)


def _build_seo_description(event):
    text = event.short_description or event.full_description or event.title
    text = " ".join(text.split()).strip()
    if len(text) <= 155:
        return text
    return f"{text[:152].rsplit(' ', 1)[0]}..."


def _build_location_label(event):
    chunks = [event.venue, event.municipality]
    return ", ".join(part for part in chunks if part)


def _build_search_document(project, event):
    parts = [
        event.title,
        event.short_description,
        event.full_description,
        event.category,
        event.subcategory,
        event.municipality,
        event.venue,
        event.organizer,
        project.area_label,
        *event.tags,
    ]
    return " ".join(" ".join((part or "").split()).strip() for part in parts if part).strip()


def _build_search_boost(event):
    score = 1.0
    if event.reliability == "alta":
        score += 0.5
    elif event.reliability == "media":
        score += 0.25
    if event.image_url:
        score += 0.1
    if event.full_description:
        score += 0.15
    return round(score, 2)


def _build_analytics_labels(project, event, slug):
    return {
        "area": project.area_label,
        "theme": project.theme,
        "category": event.category,
        "subcategory": event.subcategory,
        "municipality": event.municipality,
        "source": event.source,
        "reliability": event.reliability,
        "slug": slug,
    }


def _build_body_markdown(event):
    lines = []
    if event.full_description:
        lines.append(event.full_description)
    metadata = []
    if event.start_date:
        metadata.append(f"- Data inizio: {event.start_date}")
    if event.end_date:
        metadata.append(f"- Data fine: {event.end_date}")
    if event.time_text:
        metadata.append(f"- Ora: {event.time_text}")
    if event.venue:
        metadata.append(f"- Luogo: {event.venue}")
    if event.municipality:
        metadata.append(f"- Comune: {event.municipality}")
    if event.organizer:
        metadata.append(f"- Organizzatore: {event.organizer}")
    if event.source_url:
        metadata.append(f"- Fonte originale: {event.source_url}")
    if metadata:
        lines.append("")
        lines.append("## Dettagli")
        lines.extend(metadata)
    return "\n".join(lines).strip()
