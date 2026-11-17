import html
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from dashboard.queries import (
    get_candidates,
    get_videos_for_candidates,
    get_kpis,
    get_category_counts,
    get_quadrant_counts,
    get_run_history,
    get_last_run_time,
)
from dashboard.charts import category_donut, quadrant_bar
from scraper.filters import is_global_portable
from scraper.hooks import matches_hook_phrases
from analytics.trending import (
    is_early_breakout,
    video_age_days,
    apply_cluster_bonuses,
)


def _int(val, default=0) -> int:
    try:
        return int(float(val)) if val is not None else default
    except Exception:
        return default


def _float(val, default=0.0) -> float:
    try:
        return float(val) if val is not None else default
    except Exception:
        return default


_QUAD_BADGE_STYLES = {
    "VIRAL_GOLD": "background:#3b2f00;color:#ffd700;border:1px solid #ffd700;",
    "SLEEPER_HIT": "background:#003322;color:#00ff88;border:1px solid #00ff88;",
    "VIRAL_RISK": "background:#3b0d0d;color:#ff6b6b;border:1px solid #ff6b6b;",
    "ARCHIVE": "background:#262730;color:#a0a4ab;border:1px solid #555;",
}

_TABLE_CSS = """
<style>
.radar-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    text-align: left;
    color: #e0e0e0;
}
.radar-table thead th {
    position: sticky;
    top: 0;
    background: #1E1E24;
    z-index: 2;
    border-bottom: 2px solid #333;
    padding: 12px 10px;
    font-weight: 600;
    color: #fafafa;
}
.radar-table tbody tr {
    border-bottom: 1px solid #262730;
    transition: background-color 0.15s ease;
}
.radar-table tbody tr:hover {
    background-color: #2b2d35;
}
.radar-table td {
    padding: 10px;
    vertical-align: middle;
}
.badge {
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
}
.desc-link {
    color: #e0e0e0;
    text-decoration: none;
    transition: color 0.2s ease;
    display: inline-block;
}
.desc-link:hover {
    color: #4ECDC4;
}
.link-icon {
    color: #4ECDC4;
    font-size: 13px;
    margin-left: 5px;
    font-weight: bold;
}
.thumb-link {
    display: inline-block;
    cursor: zoom-in;
}
.thumb-img {
    width: 60px;
    height: 80px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #333;
    display: block;
    background: #1a1b20;
    transition: transform 0.15s ease, border-color 0.15s ease;
}
.thumb-link:hover .thumb-img {
    transform: scale(1.08);
    border-color: #4ECDC4;
}
.thumb-empty {
    width: 60px;
    height: 80px;
    border-radius: 6px;
    border: 1px dashed #333;
    background: #1a1b20;
    color: #666;
    font-size: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}
</style>
"""


def _render_html_candidates_table(rows: list) -> str:
    """Render a fast, scrollable, styled DOM table."""
    body_cells = []
    for r in rows:
        quad = html.escape(str(r["Quadrant"]))
        q_style = _QUAD_BADGE_STYLES.get(r["Quadrant"], "")
        cat = html.escape(str(r["Category"]))
        signals = html.escape(str(r["Signals"]))
        source = html.escape(str(r["Source"]))
        desc = html.escape(str(r["Description"]))
        author = html.escape(str(r["Author"]))
        link = html.escape(str(r["Link"]))
        cover = html.escape(str(r.get("Cover") or ""))

        if cover:
            thumb_html = (
                f'<a href="{cover}" target="_blank" rel="noopener noreferrer" '
                f'class="thumb-link" title="Open full-size image">'
                f'<img src="{cover}" class="thumb-img" loading="lazy" '
                f'onerror="this.style.display=\'none\';this.parentElement.nextElementSibling.style.display=\'flex\';">'
                f'</a>'
                f'<div class="thumb-empty" style="display:none;">No Img</div>'
            )
        else:
            thumb_html = '<div class="thumb-empty">No Img</div>'

        desc_html = (
            f'<a href="{link}" target="_blank" class="desc-link">{desc}<span class="link-icon">↗</span></a>'
            if link else desc
        )

        body_cells.append(
            f"<tr>"
            f"<td style='text-align:right;color:#888;'>{r['Rank']}</td>"
            f"<td>{thumb_html}</td>"
            f"<td><code>{cat}</code></td>"
            f"<td><span class='badge' style='{q_style}'>{quad}</span></td>"
            f"<td style='text-align:right;font-weight:700;color:#fff;'>{r['Score']:.2f}</td>"
            f"<td style='text-align:right;'>{html.escape(str(r['Age']))}</td>"
            f"<td style='text-align:center;'>{html.escape(str(r['Cluster']))}</td>"
            f"<td style='text-align:right;'>{r['Views']:,}</td>"
            f"<td style='text-align:right;'>{r['Vel/hr']:,}</td>"
            f"<td style='text-align:right;'>{r['Eng%']:.2f}%</td>"
            f"<td style='text-align:right;color:#4ECDC4;font-weight:600;'>{r['Saves']:,}</td>"
            f"<td style='font-size:12px;color:#ffd166;'>{signals}</td>"
            f"<td style='font-size:12px;color:#95a5a6;'>{source}</td>"
            f"<td style='max-width:350px;font-size:13px;line-height:1.4;'>{desc_html}</td>"
            f"<td style='font-size:12px;'>@{author}</td>"
            f"</tr>"
        )

    return (
        f"{_TABLE_CSS}"
        "<div style='max-height:750px;overflow-y:auto;overflow-x:auto;border:1px solid #333;border-radius:8px;background:#111;'>"
        "<table class='radar-table'>"
        "<thead><tr>"
        "<th style='text-align:right;'>#</th>"
        "<th>Preview</th>"
        "<th>Category</th>"
        "<th>Quadrant</th>"
        "<th style='text-align:right;'>Score</th>"
        "<th style='text-align:right;'>Age</th>"
        "<th style='text-align:center;'>Cluster</th>"
        "<th style='text-align:right;'>Views</th>"
        "<th style='text-align:right;'>Vel/hr</th>"
        "<th style='text-align:right;'>Eng%</th>"
        "<th style='text-align:right;'>Saves</th>"
        "<th>Signals</th>"
        "<th>Source</th>"
        "<th>Description</th>"
        "<th>Author</th>"
        "</tr></thead>"
        f"<tbody>{''.join(body_cells)}</tbody>"
        "</table></div>"
    )


st.set_page_config(page_title="TikTok Lighting Scraper", page_icon="💡", layout="wide")
st.title("TikTok Lighting Product Intelligence")

last_run = get_last_run_time()
if last_run:
    st.caption(f"Last Scrape Completed: {last_run}")

tab_radar, tab_stats = st.tabs(["🎯 Product Radar", "⚙️ System Stats"])

with tab_radar:
    cat_counts = get_category_counts()
    quad_counts = get_quadrant_counts()

    st.markdown("### 🎛️ Discovery Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 1.3, 1.3])
    with col_f1:
        all_categories = list(cat_counts.keys())
        selected_categories = st.multiselect("Category", all_categories, default=all_categories)
    with col_f2:
        all_quadrants = list(quad_counts.keys())
        default_quads = [q for q in all_quadrants if q != "ARCHIVE"] or all_quadrants
        selected_quadrants = st.multiselect("Quadrant", all_quadrants, default=default_quads)
    with col_f3:
        only_ads_sellers = st.checkbox("Active Ads / Sellers only", value=False)
        only_portable = st.checkbox("Global USB/Cordless only", value=False)
    with col_f4:
        only_breakout = st.checkbox("Breakout (<14 days) only", value=False)
        only_clusters = st.checkbox("Multi-Video Clusters (2+)", value=False)

    max_rows = st.selectbox("Max rows to display", [100, 250, 500, 2000], index=1)

    candidates = get_candidates(
        category=selected_categories if selected_categories else None,
        quadrant=selected_quadrants if selected_quadrants else None,
    )
    video_ids = [c["video_id"] for c in candidates]
    videos = get_videos_for_candidates(video_ids)

    enriched = []
    for c in candidates:
        v = videos.get(c["video_id"], {})
        merged = dict(c)
        merged["description"] = v.get("description") or ""
        merged["author"] = v.get("author_username") or ""
        merged["video"] = v
        enriched.append(merged)

    apply_cluster_bonuses(enriched)

    rows = []
    for c in enriched:
        v = c["video"]
        is_ad_or_seller = bool(
            v.get("is_ec_video") or v.get("has_product_anchor") or v.get("author_is_seller")
        )
        portable = is_global_portable(v)
        breakout = is_early_breakout(v)
        age_d = video_age_days(v)
        cluster_sz = _int(c.get("cluster_size"), 1)

        if only_ads_sellers and not is_ad_or_seller:
            continue
        if only_portable and not portable:
            continue
        if only_breakout and not breakout:
            continue
        if only_clusters and cluster_sz < 2:
            continue

        desc_text = str(v.get("description") or "")
        hooks = matches_hook_phrases(desc_text)
        signals = []
        if breakout:
            signals.append("Breakout <14d")
        if cluster_sz > 1:
            signals.append(f"Cluster x{cluster_sz}")
        if v.get("is_ec_video") or v.get("has_product_anchor"):
            signals.append("Ad/Shop")
        if v.get("author_is_seller"):
            signals.append("Seller")
        if portable:
            signals.append("USB/Cordless")
        if hooks:
            signals.append("Hook")

        rows.append({
            "Rank": len(rows) + 1,
            "Cover": str(v.get("cover_url") or ""),
            "Category": str(c.get("category") or ""),
            "Quadrant": str(c.get("quadrant") or ""),
            "Score": _float(c.get("trending_score")),
            "Age": f"{age_d:.1f}d" if age_d < 900 else "-",
            "Cluster": f"x{cluster_sz}" if cluster_sz > 1 else "-",
            "Views": _int(v.get("views")),
            "Vel/hr": _int(round(_float(v.get("trending_velocity")))),
            "Eng%": _float(v.get("engagement_rate")),
            "Saves": _int(v.get("bookmarks")),
            "Signals": ", ".join(signals) if signals else "-",
            "Source": str(v.get("hashtag_source") or ""),
            "Description": (desc_text[:90] + "...") if len(desc_text) > 90 else desc_text,
            "Author": str(v.get("author_username") or ""),
            "Link": str(v.get("video_url") or ""),
        })

    total_matching = len(rows)
    display_rows = sorted(rows, key=lambda x: x["Score"], reverse=True)[:max_rows]

    st.markdown(f"**Showing {len(display_rows)} of {total_matching} matching candidates**")
    if display_rows:
        st.markdown(_render_html_candidates_table(display_rows), unsafe_allow_html=True)
    else:
        st.info("No candidates match the selected filters.")


with tab_stats:
    kpis = get_kpis()
    st.markdown("### 📊 Database Health")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Videos", f"{kpis['total_videos']:,}")
    col2.metric("Active Candidates", f"{kpis['total_candidates']:,}")
    col3.metric("Sleeper Hits", f"{kpis['sleeper_hits']:,}")
    col4.metric("Viral Gold", f"{kpis['viral_gold']:,}")
    col5.metric("Viral Risk", f"{kpis['viral_risk']:,}")
    col6.metric("Archived (Dead)", f"{kpis['archived']:,}")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(category_donut(cat_counts), width="stretch")
    with col_b:
        st.plotly_chart(quadrant_bar(quad_counts), width="stretch")

    st.divider()
    runs = get_run_history()
    if runs:
        st.subheader(f"Scrape Run History ({len(runs)} runs)")
        st.dataframe(pd.DataFrame(runs), width="stretch", hide_index=True)
    else:
        st.info("No scrape runs recorded yet.")
