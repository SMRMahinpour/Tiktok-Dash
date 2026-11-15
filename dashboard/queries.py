import httpx
import streamlit as st
from pathlib import Path

# Pull credentials securely from Streamlit Secrets
CF_ACCOUNT_ID = st.secrets["CF_ACCOUNT_ID"]
CF_DATABASE_ID = st.secrets["CF_DATABASE_ID"]
CF_API_TOKEN = st.secrets["CF_API_TOKEN"]
D1_API_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{CF_DATABASE_ID}/query"

_ACTIVE_WHERE = "(archived = 0 OR archived IS NULL) AND (removed = 0 OR removed IS NULL)"


def _d1_query(sql, params=None):
    """Sends a SQL query over the internet to Cloudflare D1."""
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"sql": sql}
    if params:
        payload["params"] = params
        
    with httpx.Client() as client:
        resp = client.post(D1_API_URL, headers=headers, json=payload, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success") and data.get("result"):
            return data["result"][0].get("results", [])
        return []


@st.cache_data(ttl=300)
def get_all_active_data():
    """Fetch all active candidates and their videos once every 5 minutes to save API requests."""
    cands = _d1_query(f"SELECT * FROM candidates WHERE {_ACTIVE_WHERE} ORDER BY trending_score DESC")
    if not cands:
        return [], {}
    
    # Grab the matching videos in one swift query
    vids = _d1_query(f"SELECT * FROM videos WHERE video_id IN (SELECT video_id FROM candidates WHERE {_ACTIVE_WHERE})")
    vid_dict = {v["video_id"]: v for v in vids}
    return cands, vid_dict


def get_candidates(category=None, quadrant=None):
    """Filters the cached data in-memory for instant dashboard updates."""
    cands, _ = get_all_active_data()
    res = []
    for c in cands:
        if category and c.get("category") not in category:
            continue
        if quadrant and c.get("quadrant") not in quadrant:
            continue
        res.append(c)
    return res


def get_videos_for_candidates(video_ids):
    _, vid_dict = get_all_active_data()
    return {vid: vid_dict.get(vid, {}) for vid in video_ids}


@st.cache_data(ttl=300)
def get_kpis():
    """Fetches all dashboard counts in a single lightning-fast query."""
    query = f"""
    SELECT 
        (SELECT COUNT(*) FROM videos) as total_videos,
        (SELECT COUNT(*) FROM candidates WHERE {_ACTIVE_WHERE}) as total_candidates,
        (SELECT COUNT(*) FROM candidates WHERE {_ACTIVE_WHERE} AND quadrant='SLEEPER_HIT') as sleeper_hits,
        (SELECT COUNT(*) FROM candidates WHERE archived = 1) as archived,
        (SELECT COUNT(*) FROM candidates WHERE {_ACTIVE_WHERE} AND quadrant='VIRAL_GOLD') as viral_gold,
        (SELECT COUNT(*) FROM candidates WHERE {_ACTIVE_WHERE} AND quadrant='VIRAL_RISK') as viral_risk
    """
    res = _d1_query(query)
    if res:
        return res[0]
    return {"total_videos":0, "total_candidates":0, "sleeper_hits":0, "archived":0, "viral_gold":0, "viral_risk":0}


@st.cache_data(ttl=300)
def get_category_counts():
    rows = _d1_query(f"SELECT category, COUNT(*) as cnt FROM candidates WHERE {_ACTIVE_WHERE} GROUP BY category ORDER BY cnt DESC")
    return {r["category"]: r["cnt"] for r in rows}


@st.cache_data(ttl=300)
def get_quadrant_counts():
    rows = _d1_query(f"SELECT quadrant, COUNT(*) as cnt FROM candidates WHERE {_ACTIVE_WHERE} GROUP BY quadrant ORDER BY cnt DESC")
    return {r["quadrant"]: r["cnt"] for r in rows}


@st.cache_data(ttl=300)
def get_run_history():
    return _d1_query("SELECT run_id, started_at, finished_at, hashtags_scraped, videos_found, alerts_sent, mode FROM scrape_runs ORDER BY run_id DESC LIMIT 50")


@st.cache_data(ttl=300)
def get_last_run_time():
    rows = _d1_query("SELECT started_at FROM scrape_runs ORDER BY run_id DESC LIMIT 1")
    return rows[0]["started_at"] if rows else None
