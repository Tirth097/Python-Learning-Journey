import streamlit as st

from utils.data_loader import load_data, apply_filters, churn_rate
from utils.styling import inject_theme, ACCENT, panel, info_tile


inject_theme()
df = load_data()

st.markdown("<h2 class='' >Key Insights &amp; Recommendations</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle' >Generated from the current data — re-run after each refresh, these numbers move with the file.</p>",
    unsafe_allow_html=True,
)

geo_filter = st.sidebar.selectbox("Geography", ["All"] + sorted(df["Geography"].unique().tolist()))
fdf = apply_filters(df, {"Geography": geo_filter})

overall_churn = churn_rate(fdf)

# ---------------------------------------------------------------------------
# Derive the findings from the data rather than hardcoding them, so this
# page stays accurate if the underlying file changes.
# ---------------------------------------------------------------------------
geo_churn = fdf.groupby("Geography")["Exited"].mean() * 100
top_geo = geo_churn.idxmax()
top_geo_rate = geo_churn.max()

age_churn = fdf.groupby("AgeGroup", observed=True)["Exited"].mean() * 100
top_age = age_churn.idxmax()
top_age_rate = age_churn.max()

active_churn = fdf.loc[fdf["IsActiveMember"] == 0, "Exited"].mean() * 100
inactive_vs_active_ratio = active_churn / max(fdf.loc[fdf["IsActiveMember"] == 1, "Exited"].mean() * 100, 0.01)

high_value = fdf[fdf["Balance"] >= fdf["Balance"].quantile(0.75)]
hv_churn_rate = churn_rate(high_value)
hv_revenue_at_risk = high_value.loc[high_value["Exited"] == 1, "Balance"].sum()

# ---------------------------------------------------------------------------
# Insight cards
# ---------------------------------------------------------------------------
st.markdown('<div class="panel-title" style="font-size:18px; margin-bottom:14px;">Key Insights</div>', unsafe_allow_html=True)

i1, i2 = st.columns(2)
with i1:
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['red']};">
            <b style="color:#f8fafc;">{top_geo} leads in churn</b><br>
            <span style="color:#94a3b8;">
            {top_geo} shows the highest churn rate at <b>{top_geo_rate:.2f}%</b>,
            against an overall rate of {overall_churn:.2f}% across the filtered base.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['orange']};">
            <b style="color:#f8fafc;">{top_age} customers are the highest-risk age band</b><br>
            <span style="color:#94a3b8;">
            Churn among this group runs at <b>{top_age_rate:.2f}%</b>, the steepest of any age segment,
            suggesting retention messaging tuned to this stage of life is worth testing.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with i2:
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['teal']};">
            <b style="color:#f8fafc;">Inactive members churn far more than active ones</b><br>
            <span style="color:#94a3b8;">
            Inactive members churn at roughly <b>{inactive_vs_active_ratio:.1f}x</b> the rate of active members —
            activity status is one of the strongest single signals in this dataset.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['purple']};">
            <b style="color:#f8fafc;">High-value customers carry real revenue risk</b><br>
            <span style="color:#94a3b8;">
            The top balance quartile churns at <b>{hv_churn_rate:.1f}%</b>, putting roughly
            <b>€{hv_revenue_at_risk/1e6:.1f}M</b> in balances at risk from customers who have already left.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Recommendations 
# ---------------------------------------------------------------------------
st.markdown('<div class="panel-title" style="font-size:18px; margin-bottom:14px;">Recommendations</div>', unsafe_allow_html=True)

r1, r2 = st.columns(2)
with r1:
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Prioritize {top_geo} for retention outreach</b><br>
            <span style="color:#94a3b8;">
            Given the {top_geo_rate:.1f}% churn rate, a targeted retention campaign here would
            address the single largest regional gap before broader rollout elsewhere.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Build a re-engagement trigger for inactive members</b><br>
            <span style="color:#94a3b8;">
            Since inactivity tracks so closely with churn, an automated nudge (app login streaks,
            transaction reminders) for members inactive 60+ days could catch risk before it becomes churn.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r2:
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Protect the high-value segment with a dedicated program</b><br>
            <span style="color:#94a3b8;">
            With €{hv_revenue_at_risk/1e6:.1f}M already at risk in this segment, a relationship-manager
            check-in for the top balance quartile is a defensible ask given the revenue exposure.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Test age-tailored product bundling for {top_age}</b><br>
            <span style="color:#94a3b8;">
            This band's churn rate stands out enough to justify a controlled A/B test on
            products or pricing tailored to this life stage before wider investment.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    "These insights are computed live from the loaded CSV."
)