import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_data, apply_filters, apply_date_range
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template

inject_theme()
df = load_data()

st.markdown("<h2>CBP vs. HHS Load Comparison</h2>", unsafe_allow_html=True)
st.markdown("<p class='dash-subtitle'>Where the care burden sits across the two custody systems, and how it has shifted over time.</p>", unsafe_allow_html=True)

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
year_filter = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
fdf = apply_filters(df, {"Year": year_filter})
if isinstance(date_range, tuple) and len(date_range) == 2:
    fdf = apply_date_range(fdf, date_range[0], date_range[1])

# KPI row per system
k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Avg. CBP Custody", f"{fdf['CBP_Custody'].mean():,.0f}", f"{fdf['CBP_Custody'].mean()/fdf['TotalSystemLoad'].mean()*100:.1f}% of total load", delta_positive=False)
with k2:
    kpi_card("Avg. HHS Care", f"{fdf['HHS_Care'].mean():,.0f}", f"{fdf['HHS_Care'].mean()/fdf['TotalSystemLoad'].mean()*100:.1f}% of total load")
with k3:
    kpi_card("Avg. Total System Load", f"{fdf['TotalSystemLoad'].mean():,.0f}", "CBP + HHS combined")

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    with panel("CBP Custody vs. HHS Care Over Time"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["CBP_Custody"], mode="lines", name="CBP Custody",
                                  line=dict(color=ACCENT["orange"], width=1.5)))
        fig.add_trace(go.Scatter(x=fdf["Date"], y=fdf["HHS_Care"], mode="lines", name="HHS Care",
                                  line=dict(color=ACCENT["teal"], width=1.5)))
        fig.update_layout(template=plotly_template(), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Children", height=360, legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, use_container_width=True)

with right:
    with panel("Average Monthly Custody Split"):
        monthly = fdf.groupby("MonthLabel", sort=False)[["CBP_Custody", "HHS_Care"]].mean().reset_index().tail(12)
        fig = px.bar(
            monthly, x="MonthLabel", y=["CBP_Custody", "HHS_Care"], barmode="stack",
            template=plotly_template(), color_discrete_sequence=[ACCENT["orange"], ACCENT["teal"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Avg. Children", xaxis_title=None, height=360, legend_title=None)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    with panel("CBP Intake vs. Transfers Out (Monthly Avg.)"):
        monthly_cbp = fdf.groupby("MonthLabel", sort=False)[["CBP_Intake", "CBP_Transferred"]].mean().reset_index().tail(12)
        fig = px.bar(
            monthly_cbp, x="MonthLabel", y=["CBP_Intake", "CBP_Transferred"], barmode="group",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"], ACCENT["red"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Children/day", xaxis_title=None, height=340, legend_title=None)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("Share of Total Load: CBP vs. HHS by Year"):
        year_split = fdf.groupby("Year")[["CBP_Custody", "HHS_Care"]].mean().reset_index()
        year_split["Year"] = year_split["Year"].astype(str)
        fig = px.bar(
            year_split, x="Year", y=["CBP_Custody", "HHS_Care"], barmode="stack",
            template=plotly_template(), color_discrete_sequence=[ACCENT["orange"], ACCENT["teal"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Avg. Children", xaxis_title=None, height=340, legend_title=None)
        st.plotly_chart(fig, use_container_width=True)
