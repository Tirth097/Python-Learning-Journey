import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters, apply_date_range
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template

inject_theme()
df = load_data()

st.markdown("<h2>Trends &amp; Volatility</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle'>Rolling averages, growth rate, and variability — the signals that separate a stable pipeline from a strained one.</p>",
    unsafe_allow_html=True,
)

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
load_filter = st.sidebar.selectbox("Load Level", ["All"] + df["LoadLevel"].cat.categories.tolist())
fdf = apply_filters(df, {"LoadLevel": load_filter})
if isinstance(date_range, tuple) and len(date_range) == 2:
    fdf = apply_date_range(fdf, date_range[0], date_range[1])

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
most_volatile_year = df.groupby("Year")["RollingStd7"].mean().idxmax()
avg_growth = fdf["CareLoadGrowthRate"].mean()

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Most Volatile Year", str(most_volatile_year))
with k2:
    kpi_card("Avg. Day-over-Day Growth", f"{avg_growth:+.2f}%", delta_positive=avg_growth <= 0)
with k3:
    avg_std = fdf["RollingStd7"].mean()
    kpi_card("Avg. 7-Day Load Std. Dev.", f"{avg_std:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Rolling average comparison + growth rate distribution
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    with panel("7-Day vs. 14-Day Rolling Average Load"):
        fig = px.line(
            fdf, x="Date", y=["Rolling7_Load", "Rolling14_Load"],
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"], ACCENT["orange"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Children", xaxis_title=None, height=340, legend_title=None)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("Day-over-Day Care Load Growth Rate"):
        fig = px.histogram(
            fdf, x="CareLoadGrowthRate", nbins=40,
            template=plotly_template(), color_discrete_sequence=[ACCENT["teal"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Reporting Days", xaxis_title="Growth Rate (%)", height=340)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Year x Quarter volatility heatmap (the interaction effect the brief calls out)
# ---------------------------------------------------------------------------
with panel("Year × Quarter — Load Volatility Heatmap"):
    heat = fdf.groupby(["Year", "Quarter"])["RollingStd7"].mean().reset_index()
    heat_pivot = heat.pivot(index="Year", columns="Quarter", values="RollingStd7")

    fig_heat = px.imshow(
        heat_pivot,
        text_auto=".0f",
        color_continuous_scale=["#3b82f6", "#a855f7", "#ef4565"],
        template=plotly_template(),
        aspect="auto",
    )
    fig_heat.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        coloraxis_showscale=True,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Distribution view — box plot of total load by strain status
# ---------------------------------------------------------------------------
with panel("Total System Load Distribution — Strain vs. Normal/Relief"):
    fig_box = px.box(
        fdf, x="StrainLabel", y="TotalSystemLoad", color="StrainLabel",
        template=plotly_template(),
        color_discrete_map={"Strain": ACCENT["red"], "Normal/Relief": ACCENT["teal"]},
    )
    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           showlegend=False, xaxis_title=None, height=320)
    st.plotly_chart(fig_box, use_container_width=True)
