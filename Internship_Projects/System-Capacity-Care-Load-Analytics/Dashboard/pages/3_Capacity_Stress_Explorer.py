import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template

inject_theme()
df = load_data()

st.markdown("<h2>Capacity Stress Explorer</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle'>Isolating the highest-load reporting days — the windows that matter most for staffing and shelter planning.</p>",
    unsafe_allow_html=True,
)

threshold_pct = st.sidebar.slider(
    "High-load threshold (system load percentile)", min_value=50, max_value=95, value=75, step=5,
    help="Reporting days at or above this total-system-load percentile are treated as 'high stress'.",
)
year_filter = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
fdf = apply_filters(df, {"Year": year_filter})

load_cutoff = fdf["TotalSystemLoad"].quantile(threshold_pct / 100)
high_stress = fdf[fdf["TotalSystemLoad"] >= load_cutoff]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("High-Stress Days", f"{len(high_stress):,}", f"{len(high_stress)/len(fdf)*100:.1f}% of period")
with k2:
    kpi_card("Avg. Load (High-Stress)", f"{high_stress['TotalSystemLoad'].mean():,.0f}" if len(high_stress) else "0",
              f"vs {fdf['TotalSystemLoad'].mean():,.0f} overall", delta_positive=False)
with k3:
    strain_share_hs = (high_stress["StrainLabel"] == "Strain").mean() * 100 if len(high_stress) else 0.0
    kpi_card("Share Also Flagged 'Strain'", f"{strain_share_hs:.1f}%", "of high-stress days")
with k4:
    kpi_card("Avg. Net Intake (High-Stress)", f"{high_stress['NetDailyIntake'].mean():+.1f}" if len(high_stress) else "0")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CBP custody vs HHS care scatter, colored by strain — shows if it's a CBP
# story, an HHS story, or both
# ---------------------------------------------------------------------------
with panel("CBP Custody vs. HHS Care — High-Stress Segment"):
    fig_scatter = px.scatter(
        high_stress, x="CBP_Custody", y="HHS_Care", color="StrainLabel",
        template=plotly_template(), opacity=0.65,
        color_discrete_map={"Strain": ACCENT["red"], "Normal/Relief": ACCENT["teal"]},
    )
    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# High-stress breakdown: by weekday and by quarter
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    with panel("High-Stress Days by Weekday"):
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        wd = high_stress["WeekdayName"].value_counts().reindex(weekday_order).fillna(0).reset_index()
        wd.columns = ["WeekdayName", "days"]
        fig = px.bar(wd, x="WeekdayName", y="days", template=plotly_template(),
                     color_discrete_sequence=[ACCENT["purple"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="High-Stress Days", height=320, xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("High-Stress Days by Quarter"):
        q = high_stress["Quarter"].value_counts().reset_index()
        q.columns = ["Quarter", "days"]
        fig = px.bar(q.sort_values("Quarter"), x="Quarter", y="days", template=plotly_template(),
                     color_discrete_sequence=[ACCENT["orange"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="High-Stress Days", height=320, xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Drill-down table of high-stress, backlog-building days (priority list)
# ---------------------------------------------------------------------------
with panel("Priority Watch List (High-Stress + Backlog Building)"):
    watch = high_stress[high_stress["BacklogLabel"] == "Backlog Building"].sort_values(
        "TotalSystemLoad", ascending=False
    )
    st.dataframe(
        watch[["Date", "CBP_Custody", "HHS_Care", "TotalSystemLoad", "NetDailyIntake", "StrainLabel"]],
        hide_index=True,
        use_container_width=True,
        height=320,
    )
    st.caption(f"{len(watch):,} reporting days are both high-stress and building backlog — the operational priority list.")
