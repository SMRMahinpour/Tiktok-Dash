import json
import re
import time
from config import (
    MAX_AGE_MONTHS,
    AUTOMOTIVE_EXCLUSIONS,
    PRODUCT_TERMS,
    AMBIGUOUS_TERMS,
    MUSIC_CONTEXT_TERMS,
    STRONG_PRODUCT_TERMS,
    GLOBAL_PORTABLE_TERMS,
)


def _compile(terms):
    return [re.compile(r'\b' + re.escape(t) + r'\b', re.I) for t in terms]


_AUTOMOTIVE_PATTERNS = _compile(AUTOMOTIVE_EXCLUSIONS)
_PRODUCT_PATTERNS = _compile(PRODUCT_TERMS)
_AMBIGUOUS_PATTERNS = _compile(AMBIGUOUS_TERMS)
_MUSIC_PATTERNS = _compile(MUSIC_CONTEXT_TERMS)
_STRONG_PATTERNS = _compile(STRONG_PRODUCT_TERMS)
_PORTABLE_PATTERNS = _compile(GLOBAL_PORTABLE_TERMS)


def _has(patterns, text):
    return any(p.search(text) for p in patterns)


def _video_text(video):
    """Description + the video's own hashtags. Never the search tag."""
    desc = video.get("description") or ""
    tags = video.get("hashtags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [tags]
    return (desc + " " + " ".join(str(t) for t in tags)).lower()


def is_global_portable(video) -> bool:
    """True when the product is cordless/USB/rechargeable/battery-powered,
    making it easy to sell across 110V (US/CA) and 230V (UK/AU/NZ) markets."""
    return _has(_PORTABLE_PATTERNS, _video_text(video))


def is_recent_enough(video):
    created_at = int(video.get("created_at") or 0)
    if created_at <= 0:
        # Creative Center top ads and certain ad payloads omit created_at;
        # active ads are current by definition.
        return bool(video.get("is_ad") or str(video.get("hashtag_source", "")).startswith("top_ads"))
    max_age_seconds = MAX_AGE_MONTHS * 30 * 24 * 3600
    age = time.time() - created_at
    return age <= max_age_seconds


def _extract_source_token(raw_source: str) -> str:
    """Strip 'related:' or 'top_ads_xx:' prefixes so seed/keyword context is preserved."""
    s = (raw_source or "").lower().strip()
    if ":" in s:
        s = s.split(":", 1)[1].strip()
    return s.lstrip("#")


def _source_counts_as_evidence(video):
    """A specific source tag (e.g. #tablelamp, related:tablelamp, top_ads_us:sconce) is evidence; #chandelier is not."""
    source = _extract_source_token(video.get("hashtag_source") or "")
    if not source:
        return False
    return _has(_PRODUCT_PATTERNS, source) and not _has(_AMBIGUOUS_PATTERNS, source)


def relevance_reason(video):
    """Return (is_relevant, reason) for diagnostics."""
    text = _video_text(video)
    if _has(_AUTOMOTIVE_PATTERNS, text):
        return False, "automotive"

    specific = _has(_PRODUCT_PATTERNS, text)
    ambiguous = _has(_AMBIGUOUS_PATTERNS, text)
    strong = _has(_STRONG_PATTERNS, text)
    source_evidence = _source_counts_as_evidence(video)

    if not specific and not ambiguous and not source_evidence:
        return False, "no_lighting_evidence"
    if _has(_MUSIC_PATTERNS, text) and not strong:
        return False, "music_no_product"
    if not specific and not source_evidence and not strong:
        return False, "ambiguous_only"
    return True, "ok"


def is_lighting_related(video):
    return relevance_reason(video)[0]


def apply_filters(videos, seen_ids):
    added = []
    stats = {
        "age_dropped": 0,
        "relevance_dropped": 0,
        "duplicates": 0,
        "reasons": {},
    }
    for v in videos:
        vid = v["video_id"]
        if vid in seen_ids:
            stats["duplicates"] += 1
            continue
        if not is_recent_enough(v):
            stats["age_dropped"] += 1
            continue
        ok, reason = relevance_reason(v)
        if not ok:
            stats["relevance_dropped"] += 1
            stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1
            continue
        seen_ids.add(vid)
        added.append(v)
    return added, stats