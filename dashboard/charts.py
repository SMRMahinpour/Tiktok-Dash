import plotly.graph_objects as go

CATEGORY_COLORS = {
    "table_lamp": "#FF6B6B",
    "pendant_ceiling": "#4ECDC4",
    "wall_sconce": "#45B7D1",
    "ambient_led": "#A78BFA",
    "other": "#95A5A6",
}

QUADRANT_COLORS = {
    "VIRAL_GOLD": "#FFD700",
    "SLEEPER_HIT": "#00FF88",
    "VIRAL_RISK": "#FF4444",
    "ARCHIVE": "#888888",
}


def category_donut(counts):
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [CATEGORY_COLORS.get(l, "#95A5A6") for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textposition="inside",
    )])
    fig.update_layout(
        title="Category Distribution",
        showlegend=True,
        height=300,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig


def quadrant_bar(counts):
    order = ["VIRAL_GOLD", "SLEEPER_HIT", "VIRAL_RISK", "ARCHIVE"]
    labels = [q for q in order if q in counts]
    values = [counts[q] for q in labels]
    colors = [QUADRANT_COLORS[q] for q in labels]

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition="auto",
    )])
    fig.update_layout(
        title="Quadrant Distribution",
        xaxis_title="Quadrant",
        yaxis_title="Count",
        height=300,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig