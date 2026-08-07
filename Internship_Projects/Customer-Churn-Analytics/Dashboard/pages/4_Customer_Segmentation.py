import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, apply_filters, churn_rate
from utils.styling import inject_theme, kpi_card, panel, ACCENT, plotly_template


inject_theme()
df = load_data()

st.markdown("<h2 class='' >Customer Segmentation</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle' >Pick a segmentation dimension and see how churn and customer volume split across it.</p>",
    unsafe_allow_html=True,
)

SEGMENT_OPTIONS = {
    "Geography": "Geography",
    "Age Group": "AgeGroup",
    "Credit Score Band": "CreditScoreBand",
    "Tenure Group": "TenureGroup",
    "Balance Segment": "BalanceSegment",
    "Gender": "Gender",
    "Number of Products": "NumOfProducts",
}

segment_label = st.sidebar.selectbox("Segment by", list(SEGMENT_OPTIONS.keys()))
segment_col = SEGMENT_OPTIONS[segment_label]

geo_filter = st.sidebar.selectbox("Geography filter", ["All"] + sorted(df["Geography"].unique().tolist()))
fdf = apply_filters(df, {"Geography": geo_filter})

# ---------------------------------------------------------------------------
# Segment table — size, churn rate, churn contribution
# ---------------------------------------------------------------------------
seg_summary = (
    fdf.groupby(segment_col, observed=True)
    .agg(customers=("Exited", "size"), churned=("Exited", "sum"))
    .reset_index()
)
seg_summary["churn_rate"] = (seg_summary["churned"] / seg_summary["customers"] * 100).round(2)
seg_summary["pct_of_base"] = (seg_summary["customers"] / len(fdf) * 100).round(1)
# Churn contribution = this segment's share of ALL churned customers, not just its own rate —
# this is what separates "high churn rate" from "where most of the churn volume actually sits"
total_churned = seg_summary["churned"].sum()
seg_summary["churn_contribution_pct"] = (seg_summary["churned"] / total_churned * 100).round(1) if total_churned else 0

k1, k2, k3 = st.columns(3)
with k1:
    riskiest = seg_summary.sort_values("churn_rate", ascending=False).iloc[0]
    kpi_card(f"Highest Churn Rate — {segment_label}", f"{riskiest[segment_col]}: {riskiest['churn_rate']:.1f}%")
with k2:
    biggest_contributor = seg_summary.sort_values("churn_contribution_pct", ascending=False).iloc[0]
    kpi_card("Biggest Churn Contributor", f"{biggest_contributor[segment_col]}: {biggest_contributor['churn_contribution_pct']:.1f}% of all churn")
with k3:
    kpi_card("Segments in View", f"{len(seg_summary)}")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns([1.2, 1])

with c1:
    with panel(f"Churn Rate by {segment_label}"):
        fig = px.bar(
            seg_summary.sort_values("churn_rate", ascending=False),
            x=segment_col, y="churn_rate",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
            text="churn_rate",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_title="Churn Rate (%)", xaxis_title=None, height=380)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    with panel("Segment Size (% of Base)"):
        fig = px.pie(
            seg_summary, names=segment_col, values="customers", hole=0.5,
            template=plotly_template(),
            color_discrete_sequence=[ACCENT["blue"], ACCENT["red"], ACCENT["teal"], ACCENT["orange"], ACCENT["purple"], ACCENT["green"]],
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=380, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Full segment table — this is the number stakeholders actually ask for:
# "which segment is driving the most churn volume, not just rate"
# ---------------------------------------------------------------------------
with panel("Segment Detail Table"):
    display_table = seg_summary.rename(columns={
        segment_col: segment_label,
        "customers": "Customers",
        "churned": "Churned Count",
        "churn_rate": "Churn Rate (%)",
        "pct_of_base": "% of Customer Base",
        "churn_contribution_pct": "% of Total Churn",
    }).sort_values("Churn Rate (%)", ascending=False)
    st.dataframe(display_table, hide_index=True, use_container_width=True)