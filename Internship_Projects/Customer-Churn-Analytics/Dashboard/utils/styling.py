"""
Theme engine + reusable UI pieces for the churn dashboard.

Import inject_theme() once per page render (it's cheap/idempotent) and use
panel(title, icon) as a context manager instead of hand-rolling
<div class="panel-card"> markup — Streamlit renders every st.markdown() call
as an independent DOM node, so a div opened in one call and "closed" in a
later call never actually wraps the elements in between. panel() uses
st.container(key=...) instead, which Streamlit really does render as one
wrapping element, so the CSS below actually applies to its contents.
"""

from contextlib import contextmanager

import numpy as np
import streamlit as st

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
ACCENT = {
    "red": "#ef4565",
    "blue": "#3b82f6",
    "teal": "#14b8a6",
    "purple": "#a855f7",
    "orange": "#f59e0b",
    "green": "#22c55e",
}

PLOTLY_TEMPLATE = "plotly_dark"  # kept as a module-level default; Overview overrides per theme

_THEMES = {
    "dark": {
        "bg_app": "#0b1220",
        "bg_card": "#131b2e",
        "bg_card_alt": "#0f1729",
        "border": "#22304a",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "plotly_template": "plotly_dark",
    },
    "light": {
        "bg_app": "#f2f5fb",
        "bg_card": "#ffffff",
        "bg_card_alt": "#f8fafc",
        "border": "#e2e8f0",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "plotly_template": "plotly_white",
    },
}

# Sidebar stays a fixed dark "brand rail" in both themes, like the reference.
SIDEBAR_BG = "#0a0f1e"
SIDEBAR_BORDER = "#1b2740"


def get_theme() -> str:
    return st.session_state.get("theme", "dark")


def theme_vars() -> dict:
    return _THEMES[get_theme()]


def plotly_template() -> str:
    return theme_vars()["plotly_template"]


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def inject_theme():
    t = theme_vars()
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div {{
            display: flex;
            flex-direction: column;
        }}
        [data-testid="stSidebarNav"] {{
            order: 2;
        }}
        [data-testid="stSidebarUserContent"] {{
            order: 1;
        }}
      
        .stApp {{
            background-color: {t['bg_app']};
        }}
        [data-testid="stHeader"] {{
            background-color: transparent;
        }}
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: 1px solid {SIDEBAR_BORDER};
        }}
        [data-testid="stSidebar"] * {{
            color: #e2e8f0;
        }}
        [data-testid="stSidebarNav"] li div a {{
            border-radius: 10px;
            margin: 2px 10px;
            padding: 9px 12px !important;
            transition: background-color .12s ease;
        }}
        [data-testid="stSidebarNav"] li div a:hover {{
            background-color: rgba(148,163,184,0.10);
        }}
        [data-testid="stSidebarNav"] li div a[aria-current="page"] {{
            background-color: rgba(56,189,248,0.16);
        }}
        [data-testid="stSidebarNav"] li div a[aria-current="page"] span {{
            color: #38bdf8 !important;
            font-weight: 600;
        }}
        [data-testid="stSidebarNav"] {{ padding-top: 2px; }}
        .filters-head {{
            display:flex; justify-content:space-between; align-items:center;
            margin: 6px 0 6px 0; padding-top: 10px; border-top: 1px solid {SIDEBAR_BORDER};
        }}
        .filters-head span:first-child {{
            font-size: 11px; font-weight:700; letter-spacing:.06em; color:#64748b;
        }}
        [data-testid="stSidebar"] div[class*="st-key-reset_filters_btn"] button {{
            background: none !important; border: none !important; padding: 0 !important;
            color: #38bdf8 !important; font-size: 11.5px !important; min-height: 0 !important;
        }}
        h1, h2, h3, h4, p, span, label, .stMarkdown {{
            color: {t['text_primary']};
        }}
        .dash-subtitle {{
            color: {t['text_secondary']} !important;
        }}

        /* ---- KPI card ---- */
        .kpi-card {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: 14px;
            padding: 14px 16px;
            height: 100%;
        }}
        .kpi-top {{ display:flex; align-items:center; gap:10px; }}
        .kpi-icon {{
            width: 34px; height: 34px; border-radius: 50%;
            display:flex; align-items:center; justify-content:center;
            flex-shrink: 0;
        }}
        .kpi-label {{
            color: {t['text_secondary']};
            font-size: 12.5px;
            font-weight: 600;
        }}
        .kpi-value {{
            color: {t['text_primary']};
            font-size: 24px;
            font-weight: 700;
            margin-top: 8px;
        }}
        .kpi-delta-up {{ color: {ACCENT['green']}; font-size: 11.5px; font-weight: 600; }}
        .kpi-delta-down {{ color: {ACCENT['red']}; font-size: 11.5px; font-weight: 600; }}
        .kpi-spark {{ margin-top: 6px; }}

        /* ---- Panel card: generic class for self-contained inline HTML blocks
               (a single st.markdown() call that opens AND closes the div in
               one go — safe, unlike the old split-across-two-calls pattern) ---- */
        .panel-card {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: 14px;
            padding: 14px 16px;
        }}
        .panel-card b {{ color: {t['text_primary']}; }}
        .panel-card span {{ color: {t['text_secondary']}; }}

        /* ---- Panel card (via st.container(key=...)) ---- */
        div[class*="st-key-panel-"] {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: 14px;
            padding: 18px 20px 10px 20px;
        }}
        .panel-title-row {{
            display:flex; align-items:center; gap:8px;
            margin-bottom: 10px;
        }}
        .panel-title {{
            color: {t['text_primary']};
            font-size: 15px;
            font-weight: 600;
        }}
        .panel-caption {{
            color: {t['text_secondary']};
            font-size: 11.5px;
            margin: -6px 0 10px 0;
        }}

        /* ---- Insight / recommendation tiles ---- */
        .info-tile {{
            background-color: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 12px 14px;
            display:flex; gap:10px; align-items:flex-start;
        }}
        .info-tile b {{ color: {t['text_primary']}; }}
        .info-tile span {{ color: {t['text_secondary']}; font-size: 13px; }}

        .insight-tile {{
            background-color: {t['bg_card_alt']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 14px 14px 16px 14px;
            height: 100%;
        }}
        .insight-tile b {{ color: {t['text_primary']}; font-size: 13.5px; display:block; margin-bottom:4px; }}
        .insight-tile span {{ color: {t['text_secondary']}; font-size: 12.3px; line-height:1.45; }}

        .alert-box {{
            border: 1px solid {t['border']};
            border-radius: 10px;
            padding: 10px 12px;
            display:flex; gap:10px; align-items:center;
            margin-top: 10px;
        }}
        .alert-box b {{ color: {t['text_primary']}; font-size: 13px; }}
        .alert-box span {{ color: {t['text_secondary']}; font-size: 12px; }}

        /* ---- Geography table w/ inline bars ---- */
        .geo-table {{ margin-top: 4px; }}
        .geo-row {{
            display:grid; grid-template-columns: 1.1fr 1.6fr 0.8fr;
            align-items:center; gap:10px;
            padding: 9px 2px;
            border-bottom: 1px solid {t['border']};
            font-size: 13px;
        }}
        .geo-row.geo-head {{
            color: {t['text_secondary']};
            font-size: 11.5px; font-weight:600; text-transform:uppercase; letter-spacing:.03em;
            border-bottom: 1px solid {t['border']};
        }}
        .geo-row span {{ color: {t['text_primary']}; }}
        .geo-bar-wrap {{
            position:relative; background:{t['bg_card_alt']}; border-radius:6px;
            height:8px; display:flex; align-items:center;
        }}
        .geo-bar {{ height:8px; border-radius:6px; }}
        .geo-bar-wrap b {{
            position:absolute; right:0; top:-16px; font-size:12px; color:{t['text_primary']};
        }}

        /* ---- Gradient legend under the map ---- */
        .grad-legend {{
            display:flex; align-items:center; gap:8px; margin-top:8px;
            font-size:11px; color:{t['text_secondary']};
        }}
        .grad-bar {{ flex:1; height:6px; border-radius:4px; }}

        /* ---- High-value segmentation stat tiles ---- */
        .stat-tile {{
            border: 1px solid {t['border']};
            background-color: {t['bg_card_alt']};
            border-radius: 12px;
            padding: 12px 14px;
        }}
        .stat-tile-label {{ color: {t['text_secondary']}; font-size: 12px; }}
        .stat-tile-value {{ color: {t['text_primary']}; font-size: 20px; font-weight:700; margin-top:2px; }}
        .stat-tile-sub {{ font-size: 12px; font-weight:600; margin-top:2px; }}

        /* misc */
        [data-testid="stMetricValue"] {{ color: {t['text_primary']}; }}
        [data-testid="stMetricDelta"] svg {{ display:none; }}
        hr {{ border-color: {t['border']}; }}
        .brand-row {{ display:flex; align-items:center; gap:14px; padding: 10px 4px 18px 4px; }}
        .brand-title {{ font-weight:700; font-size: 17px; color:#f8fafc; line-height:1.1; }}
        .brand-sub {{ font-size: 11px; color:#94a3b8; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hand-drawn minimal icon set (24x24, stroke-based) — kept tiny on purpose,
# just enough to badge each KPI the way the reference dashboard does.
# ---------------------------------------------------------------------------
_ICON_PATHS = {
    "power": '<circle cx="12" cy="12" r="8"/><line x1="12" y1="6" x2="12" y2="12"/>',
    "users": '<circle cx="12" cy="8.2" r="3.4"/><path d="M4.5 20c0-3.7 3.2-6.4 7.5-6.4s7.5 2.7 7.5 6.4"/>',
    "user-check": '<circle cx="9.5" cy="8.2" r="3.2"/><path d="M3 20c0-3.4 2.9-5.8 6.5-5.8s6.5 2.4 6.5 5.8"/><path d="M15.5 12.5l1.8 1.8 3.2-3.6"/>',
    "user-x": '<circle cx="9.5" cy="8.2" r="3.2"/><path d="M3 20c0-3.4 2.9-5.8 6.5-5.8s6.5 2.4 6.5 5.8"/><path d="M15.5 11l5 5M20.5 11l-5 5"/>',
    "card": '<rect x="2.5" y="6" width="19" height="13" rx="2.2"/><line x1="2.5" y1="10.3" x2="21.5" y2="10.3"/>',
    "gem": '<polygon points="12,3 19.5,9 12,21 4.5,9"/>',
    "wallet": '<path d="M3.5 7.2A2.2 2.2 0 015.7 5h11.6a2.2 2.2 0 012.2 2.2v2.6h-5.3a2.6 2.6 0 000 5.2h5.3v2.8a2.2 2.2 0 01-2.2 2.2H5.7a2.2 2.2 0 01-2.2-2.2z"/>',
    "shield": '<path d="M12 3l7 3.1v5.4c0 5-3.1 7.9-7 9.2-3.9-1.3-7-4.2-7-9.2V6.1z"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><ellipse cx="12" cy="12" rx="3.4" ry="8.5"/><line x1="3.7" y1="12" x2="20.3" y2="12"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5"/>',
    "bulb": '<path d="M9 18h6M10 21h4M8 14a5 5 0 117.9 0c-.9 1.1-1.4 1.9-1.4 3.2H9.5c0-1.3-.5-2.1-1.5-3.2z"/>',
    "check-circle": '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.3l2.6 2.6 5.4-5.6"/>',
    "flag": '<line x1="5" y1="3" x2="5" y2="21"/><path d="M5 4.5h12l-3 4 3 4H5z"/>',
    "edit": '<path d="M4 20l.9-4L16 5l3 3-11.1 11L4 20z"/><line x1="13.5" y1="7.5" x2="16.5" y2="10.5"/>',
    "briefcase": '<rect x="2.5" y="8" width="19" height="12" rx="2"/><path d="M8 8V6a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="2.5" y1="13.5" x2="21.5" y2="13.5"/>',
    "alert-triangle": '<path d="M12 3.5l9.5 16.5H2.5z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="16.8" r="0.6" fill="currentColor" stroke="none"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M7.5 10.5V7a4.5 4.5 0 019 0v3.5"/>',
    "anchor": '<circle cx="12" cy="5.5" r="2.2"/><line x1="12" y1="7.7" x2="12" y2="19"/><path d="M5 13a7 7 0 0014 0"/><line x1="5" y1="13" x2="7.5" y2="13"/><line x1="16.5" y1="13" x2="19" y2="13"/>',
    "chevron-down": '<path d="M6 9l6 6 6-6"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="16" y1="3" x2="16" y2="7"/>',
    "analytics": '''
<line x1="5" y1="19" x2="5" y2="11"/>
<line x1="12" y1="19" x2="12" y2="6"/>
<line x1="19" y1="19" x2="19" y2="9"/>
<line x1="3" y1="19" x2="21" y2="19"/>
''',
    "pulse": '<path d="M2 12h4l2.5-7L13 19l2.5-7H22"/>',
}


def icon_svg(name: str, size: int = 18, color: str = "#ffffff") -> str:
    path = _ICON_PATHS.get(name, _ICON_PATHS["check-circle"])
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


def _sparkline(seed_text: str, color: str, points: int = 14, width: int = 220, height: int = 30) -> str:
    """Thin, full-width squiggle in the KPI's own accent color (matches the
    reference dashboard — the sparkline color follows the icon badge, not
    the direction of the delta)."""
    rng = np.random.default_rng(abs(hash(seed_text)) % (2**32))
    walk = np.cumsum(rng.normal(0, 1, points))
    walk = walk - walk.min()
    if walk.max() > 0:
        walk = walk / walk.max()
    xs = np.linspace(2, width - 2, points)
    ys = height - 5 - walk * (height - 10)
    # smooth with a simple quadratic-bezier-ish polyline (catmull-rom -> path)
    path = f"M {xs[0]:.1f},{ys[0]:.1f} "
    for i in range(1, len(xs)):
        mx = (xs[i - 1] + xs[i]) / 2
        path += f"Q {xs[i-1]:.1f},{ys[i-1]:.1f} {mx:.1f},{(ys[i-1]+ys[i])/2:.1f} "
    path += f"T {xs[-1]:.1f},{ys[-1]:.1f}"
    return (
        f'<svg class="kpi-spark" width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/></svg>'
    )


def kpi_card(label: str, value: str, delta: str | None = None, delta_positive: bool = True,
             icon: str = "check-circle", icon_color: str = ACCENT["blue"], sparkline: bool = True):
    """Renders one KPI tile: icon badge, label, big value, delta, sparkline.

    Built as one unbroken line (no embedded newlines) rather than a pretty
    multi-line f-string. When delta is None, {delta_html} evaluates to "" —
    if that sat on its own line in a multi-line template, it left a BLANK
    LINE in the middle of the HTML. CommonMark treats a raw HTML block as
    ending at the first blank line, so everything after it (the sparkline)
    fell out of the HTML block and got re-parsed as indented plain text,
    i.e. rendered as a literal <svg>... string in a code box instead of
    an actual image. Concatenating with no '\\n' anywhere sidesteps that
    entirely, regardless of which optional pieces are empty.
    """
    delta_html = ""
    if delta:
        cls = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'

    spark_html = _sparkline(label, icon_color) if sparkline else ""

    html = (
        '<div class="kpi-card">'
        '<div class="kpi-top">'
        f'<div class="kpi-icon" style="background-color:{icon_color};">{icon_svg(icon)}</div>'
        f'<div class="kpi-label">{label}</div>'
        '</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}'
        f'{spark_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


@contextmanager
def panel(title: str, icon: str | None = None, icon_color: str = ACCENT["blue"], caption: str | None = None,
          key: str | None = None, min_height: int | None = None):
    slug = key or "".join(ch.lower() if ch.isalnum() else "-" for ch in title)
    with st.container(key=f"panel-{slug}"):
        if min_height:
            st.markdown(
                f'<style>div[class*="st-key-panel-{slug}"] {{ min-height:{min_height}px; }}</style>',
                unsafe_allow_html=True,
            )
        icon_html = f'<span style="display:flex;">{icon_svg(icon, 16, icon_color)}</span>' if icon else ""
        st.markdown(
            f'<div class="panel-title-row">{icon_html}<div class="panel-title">{title}</div></div>',
            unsafe_allow_html=True,
        )
        if caption:
            st.markdown(f'<div class="panel-caption">{caption}</div>', unsafe_allow_html=True)
        yield


def info_tile(title: str, body: str, icon: str = "flag", icon_color: str = ACCENT["blue"]):
    st.markdown(
        f"""
        <div class="info-tile">
            <div class="kpi-icon" style="background-color:{icon_color}; width:30px; height:30px; flex-shrink:0;">
                {icon_svg(icon, 15)}
            </div>
            <div><b>{title}</b><br><span>{body}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_tile(title: str, body: str, icon: str = "flag", icon_color: str = ACCENT["blue"]):
    """Vertical tile used for the 4-across Key Insights / Recommendations rows —
    icon badge on top, title, then description underneath (matches reference)."""
    st.markdown(
        f"""
        <div class="insight-tile">
            <div class="kpi-icon" style="background-color:{icon_color}; width:30px; height:30px; margin-bottom:8px;">
                {icon_svg(icon, 15)}
            </div>
            <b>{title}</b>
            <span>{body}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_box(title: str, body: str, tone: str = "red"):
    color = ACCENT.get(tone, ACCENT["red"])
    st.markdown(
        f"""
        <div class="alert-box" style="border-color:{color}33; background-color:{color}14;">
            <div class="kpi-icon" style="background-color:{color}; width:28px; height:28px; flex-shrink:0;">
                {icon_svg('alert-triangle', 14)}
            </div>
            <div><b>{title}</b><br><span>{body}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def gradient_legend(left_label: str, right_label: str, colors=(ACCENT["blue"], ACCENT["red"])):
    st.markdown(
        f"""
        <div class="grad-legend">
            <span>{left_label}</span>
            <div class="grad-bar" style="background:linear-gradient(90deg,{colors[0]},{colors[1]});"></div>
            <span>{right_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_tile(icon: str, icon_color: str, label: str, value: str, sub: str):
    """Outlined mini tile — used for the High Value Customer Segmentation row
    (High Balance / High Salary / Premium)."""
    st.markdown(
        f"""
        <div class="stat-tile">
            <div class="kpi-icon" style="background-color:{icon_color}22; width:32px; height:32px; margin-bottom:8px;">
                <span style="display:flex;">{icon_svg(icon, 16, icon_color)}</span>
            </div>
            <div class="stat-tile-label">{label}</div>
            <div class="stat-tile-value">{value}</div>
            <div class="stat-tile-sub" style="color:{icon_color};">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def geo_table(rows: list[dict], bar_colors: dict):
    """rows: [{'name': 'Germany', 'rate': 32.44, 'customers': 2506}, ...]
    Renders a header + one row per country with an inline mini progress bar,
    matching the reference 'Churn Rate by Geography' table exactly."""
    max_rate = max(r["rate"] for r in rows) if rows else 1
    header = (
        '<div class="geo-row geo-head">'
        '<span>Country</span><span>Churn Rate</span><span style="text-align:right;">Customers</span>'
        '</div>'
    )
    body_rows = []
    for r in rows:
        pct_width = max(6, r["rate"] / max_rate * 100)
        color = bar_colors.get(r["name"], ACCENT["blue"])
        body_rows.append(
            f'<div class="geo-row">'
            f'<span>{r["name"]}</span>'
            f'<span class="geo-bar-wrap"><span class="geo-bar" style="width:{pct_width:.0f}%; background:{color};"></span>'
            f'<b>{r["rate"]:.2f}%</b></span>'
            f'<span style="text-align:right;">{r["customers"]:,}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="geo-table">{header}{"".join(body_rows)}</div>', unsafe_allow_html=True)


def filters_header():
    st.sidebar.markdown(
        '<div class="filters-head"><span>FILTERS</span></div>',
        unsafe_allow_html=True,
    )
    return st.sidebar.button("Reset All", key="reset_filters_btn")


def sidebar_brand():
    hexagon = (
        '<svg width="30" height="22" viewBox="0 0 24 24" fill="none">'
        '<path d="M12 2l8.7 5v10L12 22l-8.7-5V7z" fill="#0f766e" stroke="#2dd4bf" stroke-width="1.2"/>'
        '<path d="M12 6.5l5 3v5l-5 3-5-3v-5z" fill="none" stroke="#5eead4" stroke-width="1.3"/>'
        '</svg>'
    )
    st.sidebar.markdown(
        f"""
        <div class="brand-row">
            <div style="width:48px;height:48px;border-radius:12px;background:#0b2b28;
                        display:flex;align-items:center;justify-content:center;">{hexagon}</div>
            <div>
                <div class="brand-title">EuroBank</div>
                <div class="brand-sub">Analytics Dashboard</div>
            </div>
        </div>
        <hr style="margin:0 0 8px 0; opacity:0.25;">
        """,
        unsafe_allow_html=True,
    )


def sidebar_footer():
    st.sidebar.markdown("<hr style='opacity:0.25;'>", unsafe_allow_html=True)
    is_dark = get_theme() == "dark"
    label = "Dark mode" if is_dark else "Light mode"
    if st.sidebar.button(label, use_container_width=True, key="theme_toggle_btn"):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()
    st.sidebar.markdown(
        "<div class='brand-sub' style='text-align:center; margin-top:6px;'>EuroBank Analytics<br>© 2025 All rights reserved</div>",
        unsafe_allow_html=True,
    )
