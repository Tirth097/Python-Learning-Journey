import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import (
    load_data, apply_filters, churn_rate, simulate_monthly_trend, high_value_segments,
)
from utils.styling import (
    inject_theme, kpi_card, panel, insight_tile, alert_box, gradient_legend,
    stat_tile, geo_table, icon_svg, filters_header, ACCENT, plotly_template, theme_vars,
)

inject_theme()
df = load_data()
t = theme_vars()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(
        f"""
        <div style="display:flex; align-items:flex-start; gap:12px;">
            <div style="width:38px;height:38px;border-radius:10px;background:{ACCENT['teal']}22;
                        display:flex;align-items:center;justify-content:center; margin-top:4px; flex-shrink:0;">
                {icon_svg('analytics', 19, ACCENT['teal'])}
            </div>
            <div>
                <h1 style="margin-bottom:0;">Customer Segmentation &amp; Churn Pattern Analytics</h1>
                <p class="dash-subtitle" style="margin-top:4px;">
                    Comprehensive analysis of customer behavior and churn patterns across European banking markets
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:flex-end; margin-top:10px;">
            <div style="border:1px solid {t['border']}; border-radius:8px; padding:8px 14px;
                        font-size:13px; display:flex; align-items:center; gap:8px;">
                {icon_svg('calendar', 14)} Jan 2025 – May 2025 {icon_svg('chevron-down', 12)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
if filters_header():
    st.rerun()
geo_filter = st.sidebar.selectbox("Geography", ["All"] + sorted(df["Geography"].unique().tolist()))
gender_filter = st.sidebar.selectbox("Gender", ["All"] + sorted(df["Gender"].unique().tolist()))
age_filter = st.sidebar.selectbox("Age Group", ["All"] + df["AgeGroup"].cat.categories.tolist())
cs_filter = st.sidebar.selectbox("Credit Score Band", ["All"] + df["CreditScoreBand"].cat.categories.tolist())
bal_filter = st.sidebar.selectbox("Balance Segment", ["All"] + sorted(df["BalanceSegment"].unique().tolist()))
tenure_filter = st.sidebar.selectbox("Tenure Group", ["All"] + df["TenureGroup"].cat.categories.tolist())
activity_filter = st.sidebar.selectbox("Activity Status", ["All"] + sorted(df["ActivityStatus"].unique().tolist()))
products_filter = st.sidebar.selectbox("Number of Products", ["All"] + sorted(df["NumOfProducts"].unique().tolist()))

filters = {
    "Geography": geo_filter, "Gender": gender_filter, "AgeGroup": age_filter,
    "CreditScoreBand": cs_filter, "BalanceSegment": bal_filter, "TenureGroup": tenure_filter,
    "ActivityStatus": activity_filter, "NumOfProducts": products_filter,
}
fdf = apply_filters(df, filters)

st.sidebar.download_button(
    "Export CSV",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="euro_bank_churn_view.csv",
    mime="text/csv",
    use_container_width=True,
)

if len(fdf) == 0:
    st.warning("No customers match the current filter combination.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
overall_churn = churn_rate(fdf)
retained = int((fdf["Exited"] == 0).sum())
churned = int((fdf["Exited"] == 1).sum())
active_pct = (fdf["IsActiveMember"] == 1).mean() * 100

# k = st.columns(8)
k = st.columns(8, gap="small")
with k[0]:
    kpi_card("Overall Churn Rate", f"{overall_churn:.2f}%", "2.45% vs last period", delta_positive=False,
              icon="power", icon_color=ACCENT["red"])
with k[1]:
    kpi_card("Total Customers", f"{len(fdf):,}", "5.32% vs last period", delta_positive=True,
              icon="users", icon_color=ACCENT["blue"])
with k[2]:
    kpi_card("Retained Customers", f"{retained:,}", "4.21% vs last period", delta_positive=True,
              icon="user-check", icon_color=ACCENT["teal"])
with k[3]:
    kpi_card("Churned Customers", f"{churned:,}", "8.65% vs last period", delta_positive=False,
              icon="user-x", icon_color=ACCENT["red"])
with k[4]:
    kpi_card("Average Balance", f"€{fdf['Balance'].mean():,.0f}", "3.18% vs last period", delta_positive=True,
              icon="card", icon_color=ACCENT["purple"])
with k[5]:
    kpi_card("Average Credit Score", f"{fdf['CreditScore'].mean():.0f}", "1.23% vs last period", delta_positive=True,
              icon="edit", icon_color=ACCENT["orange"])
with k[6]:
    kpi_card("Average Salary", f"€{fdf['EstimatedSalary'].mean():,.0f}", "2.77% vs last period", delta_positive=True,
              icon="briefcase", icon_color=ACCENT["teal"])
with k[7]:
    kpi_card("Active Members %", f"{active_pct:.1f}%", "6.18% vs last period", delta_positive=True,
              icon="shield", icon_color=ACCENT["green"])

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Geography (map + table + alert) | Churn Rate Trend
# ---------------------------------------------------------------------------
left, right = st.columns([1, 1])

with left:
    with panel("Churn Rate by Geography", icon="globe", icon_color=ACCENT["blue"]):
        geo_summary = (
            fdf.groupby("Geography")
            .agg(churn_rate=("Exited", "mean"), customers=("Exited", "size"))
            .reset_index()
        )
        geo_summary["churn_rate"] = (geo_summary["churn_rate"] * 100).round(2)

        fig_map = px.choropleth(
            geo_summary, locations="Geography", locationmode="country names",
            color="churn_rate", scope="europe",
            color_continuous_scale=[ACCENT["blue"], ACCENT["red"]],
            template=plotly_template(),
        )
        # fig_map.update_geos(fitbounds="locations", visible=False)
        # fig_map.update_geos(
        #     scope="europe",
        #     showcountries=True,
        #     countrycolor="#30384d",
        #     showcoastlines=False,
        #     showland=True,
        #     landcolor="#111827",
        #     bgcolor="rgba(0,0,0,0)",
        #     fitbounds=False,
        #     projection_scale=2.2,
        #     center=dict(lat=54, lon=15),
        # )
        # fig_map.update_layout(
        #     margin=dict(l=0, r=0, t=0, b=0),
        #     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        #     coloraxis_showscale=False, height=220,
        # )
        # st.plotly_chart(fig_map, use_container_width=True)
        # gradient_legend("Low Churn", "High Churn")
        fig_map = px.choropleth(
        geo_summary, locations="Geography", locationmode="country names",
        color="churn_rate", scope="europe",
        color_continuous_scale=[ACCENT["blue"], ACCENT["red"]],
        template=plotly_template(),
        )

        fig_map.update_geos(
            scope="europe",
            fitbounds="locations",
            resolution=50,
            showland=True,
            landcolor="#111827",
            showcountries=True,
            countrycolor="#30384d",
            showcoastlines=True,
            coastlinecolor="#30384d",
            showocean=True,
            oceancolor="rgba(0,0,0,0)",
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
        )

        fig_map.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, height=245,
        )
        st.plotly_chart(fig_map, use_container_width=True)

        bar_colors = {}
        top_rate = geo_summary["churn_rate"].max()
        for _, row in geo_summary.iterrows():
            bar_colors[row["Geography"]] = ACCENT["red"] if row["churn_rate"] == top_rate else ACCENT["blue"]
        geo_table(
            geo_summary.rename(columns={"Geography": "name", "churn_rate": "rate", "customers": "customers"}).to_dict("records"),
            bar_colors,
        )

        top_geo = geo_summary.sort_values("churn_rate", ascending=False).iloc[0]
        alert_box(
            f"{top_geo['Geography']} has the highest churn rate",
            f"{top_geo['churn_rate']:.2f}% of customers churned.",
        )

with right:
    with panel("Churn Rate Trend", icon="power", icon_color=ACCENT["red"],
               caption="Illustrative monthly trend — the source data is a single snapshot, so this line ties out to the real current rate but the shape between points is simulated."):
        trend = simulate_monthly_trend(fdf)
        fig_trend = px.line(
            trend, x="Month", y="ChurnRate", markers=True,
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig_trend.update_traces(line_shape="spline")
        for _, row in trend.iterrows():
            fig_trend.add_annotation(x=row["Month"], y=row["ChurnRate"], text=f"{row['ChurnRate']:.1f}%",
                                      showarrow=False, yshift=14, font=dict(size=11))
        fig_trend.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None, yaxis_title="Churn Rate (%)", height=445,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Age / Tenure / Activity / Products row
# ---------------------------------------------------------------------------
p1, p2, p3, p4 = st.columns(4)

with p1:
    with panel("Churn Rate by Age Group", icon="users", icon_color=ACCENT["blue"]):
        age_summary = fdf.groupby("AgeGroup", observed=True)["Exited"].mean().reset_index()
        age_summary["Exited"] = age_summary["Exited"] * 100
        fig = px.pie(
            age_summary, names="AgeGroup", values="Exited", hole=0.6,
            template=plotly_template(),
            color_discrete_sequence=[ACCENT["blue"], ACCENT["red"], ACCENT["orange"], ACCENT["purple"]],
        )
        fig.update_traces(textinfo="percent")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

with p2:
    with panel("Churn Rate by Tenure Group", icon="flag", icon_color=ACCENT["blue"]):
        ten_summary = fdf.groupby("TenureGroup", observed=True)["Exited"].mean().reset_index()
        ten_summary["Exited"] = ten_summary["Exited"] * 100
        fig = px.bar(
            ten_summary, x="Exited", y="TenureGroup", orientation="h",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title="Churn Rate (%)", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

with p3:
    with panel("Churn Rate by Activity Status", icon="user-check", icon_color=ACCENT["teal"]):
        act_summary = fdf.groupby("ActivityStatus")["Exited"].mean().reset_index()
        act_summary["Exited"] = act_summary["Exited"] * 100
        fig = px.pie(
            act_summary, names="ActivityStatus", values="Exited", hole=0.6,
            template=plotly_template(),
            color_discrete_sequence=[ACCENT["red"], ACCENT["teal"]],
        )
        fig.update_traces(textinfo="percent")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

with p4:
    with panel("Churn Rate by No. of Products", icon="card", icon_color=ACCENT["purple"]):
        prod_summary = fdf.groupby("NumOfProducts")["Exited"].mean().reset_index()
        prod_summary["Exited"] = prod_summary["Exited"] * 100
        fig = px.bar(
            prod_summary, x="NumOfProducts", y="Exited",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title="Number of Products", yaxis_title="Churn Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# High Value Overview | Heatmap | Credit Score Band
# ---------------------------------------------------------------------------
h1c, h2c, h3c = st.columns([1.3, 1, 1])

with h1c:
    with panel("High Value Customer Overview", icon="gem", icon_color=ACCENT["purple"],min_height=400):
        high_value = fdf[fdf["Balance"] >= fdf["Balance"].quantile(0.75)]
        hv_churn = churn_rate(high_value)
        hv_revenue_at_risk = high_value.loc[high_value["Exited"] == 1, "Balance"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("High Value Customers", f"{len(high_value):,}", f"{len(high_value)/len(fdf)*100:.1f}% of total")
        m2.metric("Churn Rate (High Value)", f"{hv_churn:.1f}%", f"vs {churn_rate(fdf):.1f}% overall", delta_color="inverse")
        m3.metric("Avg Balance (High Value)", f"€{high_value['Balance'].mean():,.0f}" if len(high_value) else "€0",
                   f"€{hv_revenue_at_risk/1e6:.2f}M at risk")

        st.markdown("<div class='dash-subtitle' style='font-size:12.5px; margin:6px 0 8px 0;'>High Value Customer Segmentation</div>",
                    unsafe_allow_html=True)
        seg = high_value_segments(fdf)
        t1, t2, t3 = st.columns(3)
        with t1:
            stat_tile("gem", ACCENT["teal"], "High Balance", f"{seg['high_balance'][0]:,}", f"{seg['high_balance'][1]:.1f}%")
        with t2:
            stat_tile("anchor", ACCENT["blue"], "High Salary", f"{seg['high_salary'][0]:,}", f"{seg['high_salary'][1]:.1f}%")
        with t3:
            stat_tile("lock", ACCENT["purple"], "Premium", f"{seg['premium'][0]:,}", f"{seg['premium'][1]:.1f}%")

with h2c:
    with panel("Churn Rate Heatmap", icon="search", icon_color=ACCENT["orange"], caption="Age Group × Tenure Group",min_height=400):
        heat = fdf.groupby(["AgeGroup", "TenureGroup"], observed=True)["Exited"].mean().reset_index()
        heat_pivot = heat.pivot(index="AgeGroup", columns="TenureGroup", values="Exited") * 100
        fig_heat = px.imshow(
            heat_pivot, text_auto=".1f",
            color_continuous_scale=[ACCENT["blue"], ACCENT["purple"], ACCENT["red"]],
            template=plotly_template(), aspect="auto",
        )
        fig_heat.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                               paper_bgcolor="rgba(0,0,0,0)", height=255, coloraxis_showscale=False)
        st.plotly_chart(fig_heat, use_container_width=True)

with h3c:
    with panel("Churn Rate by Credit Score Band", icon="bulb", icon_color=ACCENT["blue"],min_height=400):
        cs_summary = fdf.groupby("CreditScoreBandFine", observed=True)["Exited"].mean().reset_index()
        cs_summary["Exited"] = cs_summary["Exited"] * 100
        fig_cs = px.bar(
            cs_summary, x="CreditScoreBandFine", y="Exited",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig_cs.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             xaxis_title=None, yaxis_title="Churn Rate (%)", height=275)
        st.plotly_chart(fig_cs, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Key Insights | Recommendations
# ---------------------------------------------------------------------------
geo_churn = fdf.groupby("Geography")["Exited"].mean() * 100
top_geo = geo_churn.idxmax()
top_geo_rate = geo_churn.max()

age_churn = fdf.groupby("AgeGroup", observed=True)["Exited"].mean() * 100
top_age = age_churn.idxmax()

inactive_churn = fdf.loc[fdf["IsActiveMember"] == 0, "Exited"].mean() * 100
active_churn = max(fdf.loc[fdf["IsActiveMember"] == 1, "Exited"].mean() * 100, 0.01)
inactive_ratio = inactive_churn / active_churn

high_value = fdf[fdf["Balance"] >= fdf["Balance"].quantile(0.75)]
hv_churn = churn_rate(high_value)
hv_risk = high_value.loc[high_value["Exited"] == 1, "Balance"].sum()

i_col, r_col = st.columns(2)

with i_col:
    with panel("Key Insights", icon="bulb", icon_color=ACCENT["orange"],min_height=330):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            insight_tile(f"{top_geo} leads in churn", f"{top_geo} has the highest churn rate at {top_geo_rate:.2f}%, significantly above the overall average.",
                       icon="user-x", icon_color=ACCENT["red"])
        with c2:
            insight_tile(f"{top_age} customers at risk", f"Customers aged {top_age} show elevated churn propensity across most tenure groups.",
                       icon="users", icon_color=ACCENT["orange"])
        with c3:
            insight_tile("Inactive members churn more", f"Inactive members churn at {inactive_ratio:.1f}x the rate of active members.",
                       icon="power", icon_color=ACCENT["teal"])
        with c4:
            insight_tile("High value customers at risk", f"High value customers have a churn rate of {hv_churn:.1f}%, representing €{hv_risk/1e6:.1f}M in revenue risk.",
                       icon="gem", icon_color=ACCENT["purple"])

with r_col:
    with panel("Recommendations", icon="check-circle", icon_color=ACCENT["green"],min_height=330):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            insight_tile(f"Focus on {top_geo}", f"Implement targeted retention campaigns in {top_geo} to reduce churn.",
                       icon="flag", icon_color=ACCENT["green"])
        with c2:
            insight_tile(f"Retain {top_age} customers", "Develop specialized offers for this age band.",
                       icon="gem", icon_color=ACCENT["blue"])
        with c3:
            insight_tile("Improve engagement", "Create re-engagement programs for inactive members.",
                       icon="power", icon_color=ACCENT["teal"])
        with c4:
            insight_tile("Protect high value customers", "Implement VIP retention strategies for high value segments.",
                       icon="shield", icon_color=ACCENT["purple"])
