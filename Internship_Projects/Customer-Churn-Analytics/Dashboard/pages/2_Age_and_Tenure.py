import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters, churn_rate
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template


inject_theme()
df = load_data()

st.markdown("<h2 class='' >Age &amp; Tenure Churn Comparison</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle' >Where age and relationship length compound to raise or lower churn risk.</p>",
    unsafe_allow_html=True,
)

age_filter = st.sidebar.selectbox("Age Group", ["All"] + df["AgeGroup"].cat.categories.tolist())
tenure_filter = st.sidebar.selectbox("Tenure Group", ["All"] + df["TenureGroup"].cat.categories.tolist())
fdf = apply_filters(df, {"AgeGroup": age_filter, "TenureGroup": tenure_filter})

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
oldest_band = df.groupby("AgeGroup", observed=True)["Exited"].mean().idxmax()
newest_tenure_churn = df.loc[df["TenureGroup"] == "New (<1Y)", "Exited"].mean() * 100

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Highest-Risk Age Band", str(oldest_band))
with k2:
    kpi_card("New Customer Churn (<1Y)", f"{newest_tenure_churn:.1f}%")
with k3:
    avg_tenure_churned = df.loc[df["Exited"] == 1, "Tenure"].mean()
    kpi_card("Avg. Tenure of Churners", f"{avg_tenure_churned:.1f} yrs")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Age group churn bar + tenure group churn bar
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    with panel("Churn Rate by Age Group"):
        age_summary = fdf.groupby("AgeGroup", observed=True)["Exited"].mean().reset_index()
        age_summary["Exited"] = age_summary["Exited"] * 100
        fig = px.bar(
            age_summary, x="AgeGroup", y="Exited",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", xaxis_title=None, height=340)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("Churn Rate by Tenure Group"):
        ten_summary = fdf.groupby("TenureGroup", observed=True)["Exited"].mean().reset_index()
        ten_summary["Exited"] = ten_summary["Exited"] * 100
        fig = px.bar(
            ten_summary, x="TenureGroup", y="Exited",
            template=plotly_template(), color_discrete_sequence=[ACCENT["teal"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", xaxis_title=None, height=340)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Age x Tenure heatmap (the interaction effect the brief calls out)
# ---------------------------------------------------------------------------
with panel("Age Group × Tenure Group — Churn Rate Heatmap"):

    heat = fdf.groupby(["AgeGroup", "TenureGroup"], observed=True)["Exited"].mean().reset_index()
    heat_pivot = heat.pivot(index="AgeGroup", columns="TenureGroup", values="Exited") * 100

    fig_heat = px.imshow(
        heat_pivot,
        text_auto=".1f",
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
# Distribution view — box plot of age by churn status
# ---------------------------------------------------------------------------
with panel("Age Distribution — Churned vs Retained"):
    fig_box = px.box(
        fdf, x="ChurnLabel", y="Age", color="ChurnLabel",
        template=plotly_template(),
        color_discrete_map={"Churned": ACCENT["red"], "Retained": ACCENT["teal"]},
    )
    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           showlegend=False, xaxis_title=None, height=320)
    st.plotly_chart(fig_box, use_container_width=True)