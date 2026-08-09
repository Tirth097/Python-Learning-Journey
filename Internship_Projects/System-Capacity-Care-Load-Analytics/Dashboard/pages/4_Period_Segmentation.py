import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template

inject_theme()
df = load_data()

st.markdown("<h2>Period Segmentation</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle'>Pick a time-based or capacity-based dimension and see how system load splits across it.</p>",
    unsafe_allow_html=True,
)

SEGMENT_OPTIONS = {
    "Year": "Year",
    "Quarter": "Quarter",
    "Load Level": "LoadLevel",
    "Day Type": "DayType",
    "System Status": "StrainLabel",
    "Backlog Status": "BacklogLabel",
}

segment_label = st.sidebar.selectbox("Segment by", list(SEGMENT_OPTIONS.keys()))
segment_col = SEGMENT_OPTIONS[segment_label]

year_filter = st.sidebar.selectbox("Year filter", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
fdf = apply_filters(df, {"Year": year_filter})

# ---------------------------------------------------------------------------
# Segment table — size, avg load, share of high-stress days
# ---------------------------------------------------------------------------
seg_summary = (
    fdf.groupby(segment_col, observed=True)
    .agg(
        days=("TotalSystemLoad", "size"),
        avg_load=("TotalSystemLoad", "mean"),
        strain_days=("StrainLabel", lambda s: (s == "Strain").sum()),
    )
    .reset_index()
)
seg_summary["avg_load"] = seg_summary["avg_load"].round(0)
seg_summary["pct_of_base"] = (seg_summary["days"] / len(fdf) * 100).round(1)
total_strain = seg_summary["strain_days"].sum()
seg_summary["strain_contribution_pct"] = (
    (seg_summary["strain_days"] / total_strain * 100).round(1) if total_strain else 0
)

k1, k2, k3 = st.columns(3)
with k1:
    heaviest = seg_summary.sort_values("avg_load", ascending=False).iloc[0]
    kpi_card(f"Heaviest Load — {segment_label}", f"{heaviest[segment_col]}: {heaviest['avg_load']:,.0f}")
with k2:
    biggest_contributor = seg_summary.sort_values("strain_contribution_pct", ascending=False).iloc[0]
    kpi_card("Biggest Strain Contributor", f"{biggest_contributor[segment_col]}: {biggest_contributor['strain_contribution_pct']:.1f}% of all strain days")
with k3:
    kpi_card("Segments in View", f"{len(seg_summary)}")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns([1.2, 1])

with c1:
    with panel(f"Average System Load by {segment_label}"):
        fig = px.bar(
            seg_summary.sort_values("avg_load", ascending=False),
            x=segment_col, y="avg_load",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
            text="avg_load",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Avg. System Load", xaxis_title=None, height=380)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("Segment Size (% of Reporting Days)"):
        fig = px.pie(
            seg_summary, names=segment_col, values="days", hole=0.5,
            template=plotly_template(),
            color_discrete_sequence=[ACCENT["blue"], ACCENT["red"], ACCENT["teal"], ACCENT["orange"], ACCENT["purple"], ACCENT["green"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=380, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Full segment table — "which period is driving the most strain volume,
# not just rate"
# ---------------------------------------------------------------------------
with panel("Segment Detail Table"):
    display_table = seg_summary.rename(columns={
        segment_col: segment_label,
        "days": "Reporting Days",
        "strain_days": "Strain Days",
        "avg_load": "Avg. System Load",
        "pct_of_base": "% of Days in View",
        "strain_contribution_pct": "% of Total Strain Days",
    }).sort_values("Avg. System Load", ascending=False)
    st.dataframe(display_table, hide_index=True, use_container_width=True)
