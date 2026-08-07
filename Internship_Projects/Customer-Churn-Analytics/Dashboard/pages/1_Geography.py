import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters, churn_rate
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template


inject_theme()
df = load_data()

st.markdown("<h2 class='' >Geography-Wise Churn</h2>", unsafe_allow_html=True)
st.markdown("<p class='dash-subtitle' >Regional breakdown across France, Spain and Germany.</p>", unsafe_allow_html=True)

geo_filter = st.sidebar.selectbox("Geography", ["All"] + sorted(df["Geography"].unique().tolist()))
fdf = apply_filters(df, {"Geography": geo_filter})

# KPI row per country
countries = sorted(df["Geography"].unique())
cols = st.columns(len(countries))
for col, country in zip(cols, countries):
    c_df = df[df["Geography"] == country]
    with col:
        kpi_card(country, f"{churn_rate(c_df):.2f}%", f"{len(c_df):,} customers", delta_positive=False)

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    with panel("Churn Rate by Geography &amp; Gender"):
        cross = fdf.groupby(["Geography", "Gender"])["Exited"].mean().reset_index()
        cross["Exited"] = cross["Exited"] * 100
        fig = px.bar(
            cross, x="Geography", y="Exited", color="Gender", barmode="group",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"], ACCENT["red"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", height=350)
        st.plotly_chart(fig, use_container_width=True)

with right:
    with panel("Average Balance by Geography"):
        bal = fdf.groupby("Geography")["Balance"].mean().reset_index()
        fig = px.bar(
            bal, x="Geography", y="Balance",
            template=plotly_template(), color_discrete_sequence=[ACCENT["teal"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Avg. Balance (€)", height=350)
        st.plotly_chart(fig, use_container_width=True)
