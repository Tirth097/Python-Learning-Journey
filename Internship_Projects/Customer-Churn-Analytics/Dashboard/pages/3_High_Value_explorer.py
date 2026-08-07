import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters, churn_rate
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template


inject_theme()
df = load_data()

st.markdown("<h2 class='' >High Value Customer Explorer</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle' >Isolating the customers who carry the most revenue risk if they churn.</p>",
    unsafe_allow_html=True,
)

threshold_pct = st.sidebar.slider(
    "High-value threshold (balance percentile)", min_value=50, max_value=95, value=75, step=5,
    help="Customers at or above this balance percentile are treated as 'high value'."
)
geo_filter = st.sidebar.selectbox("Geography", ["All"] + sorted(df["Geography"].unique().tolist()))
fdf = apply_filters(df, {"Geography": geo_filter})

balance_cutoff = fdf["Balance"].quantile(threshold_pct / 100)
high_value = fdf[fdf["Balance"] >= balance_cutoff]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("High Value Customers", f"{len(high_value):,}", f"{len(high_value)/len(fdf)*100:.1f}% of segment")
with k2:
    hv_churn = churn_rate(high_value)
    kpi_card("Churn Rate (High Value)", f"{hv_churn:.1f}%", f"vs {churn_rate(fdf):.1f}% overall", delta_positive=False)
with k3:
    revenue_at_risk = high_value.loc[high_value["Exited"] == 1, "Balance"].sum()
    kpi_card("Balance at Risk", f"€{revenue_at_risk/1e6:.2f}M", "sum of churned high-value balances")
with k4:
    kpi_card("Avg. Balance (High Value)", f"€{high_value['Balance'].mean():,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Balance vs Salary scatter, colored by churn — shows if it's a balance
# story, a salary story, or both
# ---------------------------------------------------------------------------
with panel("Balance vs. Estimated Salary — High Value Segment"):
    fig_scatter = px.scatter(
        high_value, x="EstimatedSalary", y="Balance", color="ChurnLabel",
        template=plotly_template(), opacity=0.6,
        color_discrete_map={"Churned": ACCENT["red"], "Retained": ACCENT["teal"]},
    )
    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# High-value segmentation: by product count and by geography
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    with panel("High Value Churn by Number of Products"):
        prod = high_value.groupby("NumOfProducts")["Exited"].mean().reset_index()
        prod["Exited"] = prod["Exited"] * 100
        fig = px.bar(prod, x="NumOfProducts", y="Exited", template=plotly_template(),
                     color_discrete_sequence=[ACCENT["purple"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", height=320)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("High Value Churn by Geography"):
        geo = high_value.groupby("Geography")["Exited"].mean().reset_index()
        geo["Exited"] = geo["Exited"] * 100
        fig = px.bar(geo, x="Geography", y="Exited", template=plotly_template(),
                     color_discrete_sequence=[ACCENT["orange"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", height=320)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Drill-down table of at-risk high value customers
# ---------------------------------------------------------------------------
with panel("At-Risk High Value Customers (Inactive + Not Yet Churned)"):
    at_risk = high_value[(high_value["IsActiveMember"] == 0) & (high_value["Exited"] == 0)].sort_values(
        "Balance", ascending=False
    )
    st.dataframe(
        at_risk[["CustomerId", "Geography", "Age", "Balance", "NumOfProducts", "EstimatedSalary", "Tenure"]],
        hide_index=True,
        use_container_width=True,
        height=320,
    )
    st.caption(f"{len(at_risk):,} high-value customers are currently inactive and have not yet churned — the retention team's priority list.")