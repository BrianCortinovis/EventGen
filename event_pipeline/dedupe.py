from typing import List

from event_pipeline.analysis import similarity
from event_pipeline.models import EventRecord


def deduplicate_events(events: List[EventRecord]) -> List[EventRecord]:
    deduped = []
    for event in events:
        merged = False
        for existing in deduped:
            if _should_merge(existing, event):
                _merge_into(existing, event)
                merged = True
                break
        if not merged:
            deduped.append(event)
    deduped.sort(key=lambda item: (item.start_date or "9999-12-31", item.municipality.lower(), item.title.lower()))
    return deduped


def _should_merge(left: EventRecord, right: EventRecord) -> bool:
    same_date = left.start_date == right.start_date and left.start_date != ""
    same_place = (left.municipality or "").lower() == (right.municipality or "").lower()
    similar_title = similarity(left.title, right.title) >= 0.84
    return same_date and same_place and similar_title


def _merge_into(target: EventRecord, incoming: EventRecord):
    if _reliability_rank(incoming.reliability) > _reliability_rank(target.reliability):
        previous_source = target.source
        target.source = incoming.source
        target.source_url = incoming.source_url
        if previous_source not in target.secondary_sources:
            target.secondary_sources.append(previous_source)
        target.reliability = incoming.reliability
        target.confirmation_status = incoming.confirmation_status
    else:
        if incoming.source not in target.secondary_sources and incoming.source != target.source:
            target.secondary_sources.append(incoming.source)

    if not target.venue and incoming.venue:
        target.venue = incoming.venue
    if not target.short_description and incoming.short_description:
        target.short_description = incoming.short_description
    if len(incoming.full_description or "") > len(target.full_description or ""):
        target.full_description = incoming.full_description
    if not target.image_url and incoming.image_url:
        target.image_url = incoming.image_url
    if not target.organizer and incoming.organizer:
        target.organizer = incoming.organizer

    target.gallery_images = sorted(set(target.gallery_images + incoming.gallery_images))
    target.flyer_urls = sorted(set(target.flyer_urls + incoming.flyer_urls))
    target.youtube_urls = sorted(set(target.youtube_urls + incoming.youtube_urls))
    target.tags = sorted(set(target.tags + incoming.tags))


def _reliability_rank(value: str) -> int:
    return {"bassa": 1, "media": 2, "alta": 3}.get(value, 0)
