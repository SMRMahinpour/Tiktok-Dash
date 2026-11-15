import math
import re
import time
from collections import defaultdict
from datetime import datetime
from config import (
    BOOKMARK_WEIGHT,
    SELLER_BONUS,
    AD_BONUS,
    HOOK_BONUS,
    GLOBAL_PORTABLE_BONUS,
    SCALE_BONUS_MAX,
    FRESHNESS_7D_BONUS,
    FRESHNESS_14D_BONUS,
    CLUSTER_BONUS_STEP,
    CLUSTER_BONUS_MAX,
)
from scraper.filters import is_global_portable

MIN_SNAPSHOT_GAP_HOURS = 6.0

_CLUSTER_STOPWORDS = frozenset({
    "the", "and", "for", "with", "this", "that", "your", "from", "you", "are",
    "have", "has", "just", "so", "too", "very", "out", "now", "new", "best",
    "link", "bio", "fyp", "foryou", "foryoupage", "viral", "tiktok", "tiktokshop",
    "tiktokmademebuyit", "homedecor", "interiordesign", "roomdecor", "home",
    "room", "light", "lights", "lighting", "lamp", "lamps",
})

_PRODUCT_DESCRIPTOR_TOKENS = frozenset({
    "mushroom", "sunset", "aurora", "galaxy", "ripple", "water", "ocean",
    "pleated", "cordless", "rechargeable", "wireless", "magnetic", "sconce",
    "pendant", "chandelier", "crystal", "feather", "cloud", "acrylic", "brass",
    "ceramic", "nordic", "japandi", "spiral", "touch", "dimmable", "donut",
    "flower", "tulip", "stained", "tiffany", "govee", "rgb", "rgbic", "neon",
    "corner", "floor", "bedside", "reading", "vanity", "picture", "globe",
})


def video_age_days(video) -> float:
    """Return video age in days from created_at Unix timestamp (or 999.0 if unknown)."""
    if not video:
        return 999.0
    created_at = int(video.get("created_at") or 0)
    if created_at <= 0:
        return 999.0
    return max((time.time() - created_at) / 86400.0, 0.0)


def is_early_breakout(video) -> bool:
    """True when a video is <= 14 days old and already showing strong traction or save intent."""
    if not video:
        return False
    age_d = video_age_days(video)
    if age_d <= 0 or age_d > 14.0:
        return False
    views = int(video.get("views") or 0)
    bookmarks = int(video.get("bookmarks") or 0)
    likes = int(video.get("likes") or 0)
    comments = int(video.get("comments") or 0)
    shares = int(video.get("shares") or 0)
    vel = float(video.get("trending_velocity") or 0.0)
    if vel <= 0 and views > 0:
        vel = views / max(age_d * 24.0, 6.0)
    eng = float(video.get("engagement_rate") or 0.0)
    if eng <= 0 and views > 0:
        eng = (likes + comments + shares) / views * 100.0
    save_rate = (bookmarks / views * 100.0) if views > 0 else 0.0
    return bool(
        views >= 10000
        and (vel >= 300.0 or bookmarks >= 300 or (eng >= 5.0 and save_rate >= 1.0))
    )


def _lifetime_velocity(current, video=None):
    """Estimate hourly velocity from video creation time when snapshot delta is unavailable."""
    if video and video.get("created_at"):
        age_hours = max((time.time() - int(video["created_at"])) / 3600, 6.0)
        cur_views = current["views"] if current is not None else 0
        return (cur_views or video.get("views") or 0) / age_hours
    return 0


def calculate_velocity(current, previous, video=None):
    """Views per hour between snapshots, protecting against TikTok's rounded view counters
    (e.g. 1.6M -> 1.6M) and short back-to-back run intervals."""
    lifetime_vel = _lifetime_velocity(current, video)

    if previous and current is not None:
        t1 = datetime.fromisoformat(str(previous["recorded_at"]).replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(str(current["recorded_at"]).replace("Z", "+00:00"))
        hours = max((t2 - t1).total_seconds() / 3600, 0.1)
        delta_views = (current["views"] or 0) - (previous["views"] or 0)

        if delta_views > 0 and hours >= MIN_SNAPSHOT_GAP_HOURS:
            return delta_views / hours

        if delta_views > 0:
            snap_vel = delta_views / hours
            return max(snap_vel, lifetime_vel)

        cur_views = current["views"] or 0
        if lifetime_vel > 0 and (hours < 24.0 or cur_views >= 10000):
            return lifetime_vel
        return delta_views / hours

    return lifetime_vel


def calculate_engagement(snapshot, video=None):
    views = max(snapshot["views"], 1)
    return (snapshot["likes"] + snapshot["comments"] + snapshot["shares"]) / views * 100


def classify_trend(velocity, engagement):
    if velocity > 50000 and engagement > 8:
        return "VIRAL"
    elif velocity > 20000 and engagement > 5:
        return "RISING_FAST"
    elif velocity > 5000 and engagement > 5:
        return "TRENDING"
    elif velocity > 1000:
        return "STABLE"
    elif velocity < 0:
        return "DYING"
    else:
        return "STAGNANT"


def classify_quadrant(velocity, engagement, video=None):
    high_v = velocity >= 500
    high_e = engagement >= 5.0

    if video:
        views = max(video.get("views", 0), 1)
        bookmarks = video.get("bookmarks", 0)
        save_rate_pct = (bookmarks / views) * 100.0
        has_commerce_signal = bool(
            video.get("is_ad") or video.get("is_ec_video") or video.get("author_is_seller")
        )
        is_scaled_product = has_commerce_signal or (bookmarks >= 1500 and save_rate_pct >= 0.5)
        if views >= 500000 and is_scaled_product:
            if (bookmarks >= 2000 and save_rate_pct >= 0.4) or engagement >= 2.0:
                return "VIRAL_GOLD"
            return "VIRAL_RISK"
        if views >= 150000 and bookmarks >= 1000 and save_rate_pct >= 0.5 and engagement >= 2.5:
            return "VIRAL_GOLD" if high_v else "SLEEPER_HIT"

    if high_v and high_e:
        return "VIRAL_GOLD"
    elif not high_v and high_e:
        return "SLEEPER_HIT"
    elif high_v and not high_e:
        return "VIRAL_RISK"
    return "ARCHIVE"

def trending_score(velocity, engagement, video=None):
    """Composite product-opportunity score (0-14+ scale)."""
    base = min(max(velocity, 0) / 1000, 10) * 0.30 + min(max(engagement, 0), 10) * 0.40

    if video:
        bookmarks = video.get("bookmarks", 0)
        views = max(video.get("views", 1), 1)
        likes = max(video.get("likes", 1), 1)

        view_scale = min(math.log10(max(views, 1000) / 1000) * 0.65, SCALE_BONUS_MAX)
        save_scale = min(math.log10(max(bookmarks, 10) / 10) * 0.40, 1.4)
        base += view_scale + save_scale

        view_save_pct = min((bookmarks / views) * 100, 5.0)
        like_save_pct = min((bookmarks / likes) * 10, 5.0)
        base += (view_save_pct + like_save_pct) * BOOKMARK_WEIGHT

        if video.get("author_is_seller", False):
            base += SELLER_BONUS
        if video.get("is_ad", False) or video.get("is_ec_video", False) or video.get("has_product_anchor", False):
            base += AD_BONUS
        if video.get("hook_matches"):
            base += HOOK_BONUS
        if is_global_portable(video):
            base += GLOBAL_PORTABLE_BONUS

        age_d = video_age_days(video)
        if 0 < age_d <= 7.0:
            base += FRESHNESS_7D_BONUS
        elif 7.0 < age_d <= 14.0:
            base += FRESHNESS_14D_BONUS

    return base


def _product_signature(candidate: dict) -> str:
    """Build a canonical product signature from category + key product descriptor tokens."""
    cat = candidate.get("category") or "other"
    desc = (candidate.get("description") or "").lower()
    words = re.findall(r"[a-z0-9]+", desc)
    matched = sorted({
        w for w in words
        if w in _PRODUCT_DESCRIPTOR_TOKENS and w not in _CLUSTER_STOPWORDS
    })
    if len(matched) >= 2:
        return f"{cat}:{'+'.join(matched[:4])}"
    return ""


def apply_cluster_bonuses(candidates: list) -> list:
    """Detect repeated products (by product signature) or multi-video active sellers,
    annotate `cluster_size` and `cluster_key`, and award up to CLUSTER_BONUS_MAX."""
    if not candidates:
        return candidates

    sig_groups = defaultdict(list)
    author_groups = defaultdict(list)

    for idx, c in enumerate(candidates):
        sig = _product_signature(c)
        if sig:
            sig_groups[sig].append(idx)
        author = (c.get("author") or c.get("author_username") or "").strip().lower()
        if author and author not in ("tiktok", "unknown"):
            author_groups[author].append(idx)

    for idx, c in enumerate(candidates):
        sig = _product_signature(c)
        author = (c.get("author") or c.get("author_username") or "").strip().lower()
        sig_members = sig_groups.get(sig, []) if sig else []
        auth_members = author_groups.get(author, []) if author else []

        if len(sig_members) >= len(auth_members) and len(sig_members) > 1:
            cluster_size = len(sig_members)
            cluster_key = sig
        elif len(auth_members) > 1:
            cluster_size = len(auth_members)
            cluster_key = f"seller:@{author}"
        else:
            cluster_size = 1
            cluster_key = sig or (f"seller:@{author}" if author else "")

        c["cluster_size"] = cluster_size
        c["cluster_key"] = cluster_key
        if cluster_size > 1:
            bonus = min((cluster_size - 1) * CLUSTER_BONUS_STEP, CLUSTER_BONUS_MAX)
            c["trending_score"] = round(float(c.get("trending_score", 0.0)) + bonus, 4)

    return candidates


def should_alert(video, trend_level, thresholds):
    has_product = (
        video.get("has_product_anchor", False)
        or video.get("is_ad", False)
        or video.get("is_ec_video", False)
        or video.get("author_is_seller", False)
    )
    views = video.get("views", 0)
    engagement = video.get("engagement_rate", 0)
    if trend_level in ("VIRAL", "RISING_FAST") and has_product:
        return True, "viral_product"
    if views >= thresholds.get("min_views", 50000) and engagement >= thresholds.get("min_engagement_rate", 5.0):
        return True, "trending"
    if video.get("is_ad", False) and views >= 25000 and engagement >= 4.0:
        return True, "rising"
    return False, None