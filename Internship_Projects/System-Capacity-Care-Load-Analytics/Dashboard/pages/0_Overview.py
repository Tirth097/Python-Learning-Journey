import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import (
    load_data, apply_filters, apply_date_range, net_intake_pressure,
    care_load_volatility, discharge_offset_ratio, backlog_accumulation_rate, strain_share,
)
from utils.styling import (
    inject_theme, kpi_card, panel, insight_tile, alert_box,
    stat_tile, icon_svg, filters_header, ACCENT, plotly_template, theme_vars,
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
                <h1 style="margin-bottom:0;">System Capacity &amp; Care Load Analytics</h1>
                <p class="dash-subtitle" style="margin-top:4px;">
                    Monitoring the CBP-to-HHS care pipeline for unaccompanied children: intake, custody, transfer, and discharge load
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
                {icon_svg('calendar', 14)} Jan 2023 – Dec 2025 {icon_svg('chevron-down', 12)}
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

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
year_filter = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
load_filter = st.sidebar.selectbox("Load Level", ["All"] + df["LoadLevel"].cat.categories.tolist())
strain_filter = st.sidebar.selectbox("System Status", ["All"] + sorted(df["StrainLabel"].unique().tolist()))
backlog_filter = st.sidebar.selectbox("Backlog Status", ["All"] + sorted(df["BacklogLabel"].unique().tolist()))
daytype_filter = st.sidebar.selectbox("Day Type", ["All"] + sorted(df["DayType"].unique().tolist()))

filters = {
    "Year": year_filter, "LoadLevel": load_filter, "StrainLabel": strain_filter,
    "BacklogLabel": backlog_filter, "DayType": daytype_filter,
}
fdf = apply_filters(df, filters)
if isinstance(date_range, tuple) and len(date_range) == 2:
    fdf = apply_date_range(fdf, date_range[0], date_range[1])

st.sidebar.download_button(
    "Export CSV",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="uac_care_load_view.csv",
    mime="text/csv",
    use_container_width=True,
)

if len(fdf) == 0:
    st.warning("No reporting days match the current filter combination.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_under_care = fdf["TotalSystemLoad"].iloc[-1]
avg_load = fdf["TotalSystemLoad"].mean()
net_pressure = net_intake_pressure(fdf)
volatility = care_load_volatility(fdf)
backlog_rate = backlog_accumulation_rate(fdf)
offset_ratio = discharge_offset_ratio(fdf)
strain_pct = strain_share(fdf)

k = st.columns(7, gap="small")
with k[0]:
    kpi_card("Total Children Under Care", f"{total_under_care:,.0f}", "latest reporting day",
              delta_positive=False, icon="users", icon_color=ACCENT["blue"])
with k[1]:
    kpi_card("Avg. System Load", f"{avg_load:,.0f}", "CBP + HHS, period avg",
              icon="shield", icon_color=ACCENT["purple"])
with k[2]:
    kpi_card("Net Intake Pressure", f"{net_pressure:+.1f}/day", "transfers − discharges",
              delta_positive=net_pressure <= 0, icon="power", icon_color=ACCENT["red"])
with k[3]:
    kpi_card("Care Load Volatility", f"{volatility:.1f}%", "7-day std / mean load",
              delta_positive=False, icon="pulse", icon_color=ACCENT["orange"])
with k[4]:
    kpi_card("Backlog Accumulation", f"{backlog_rate:+.2f}/day", "avg. change in 14-report backlog",
              delta_positive=backlog_rate <= 0, icon="anchor", icon_color=ACCENT["teal"])
with k[5]:
    kpi_card("Discharge Offset Ratio", f"{offset_ratio:.1f}%", "discharges vs. transfers in",
              icon="user-check", icon_color=ACCENT["green"])
with k[6]:
    kpi_card("Days Under Strain", f"{strain_pct:.1f}%", "of reporting days in view",
              delta_positive=False, icon="alert-triangle", icon_color=ACCENT["red"])

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# System load trend | CBP vs HHS load composition
# ---------------------------------------------------------------------------
left, right = st.columns([1.3, 1])

with left:
    with panel("Total System Load Over Time", icon="analytics", min_height=560, icon_color=ACCENT["blue"],
               caption="Daily total (CBP custody + HHS care) with 7-day and 14-day rolling averages."):
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=fdf["Date"], y=fdf["TotalSystemLoad"], mode="lines",
                                        name="Daily Total", line=dict(color=ACCENT["blue"], width=1), opacity=0.4))
        fig_trend.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Rolling7_Load"], mode="lines",
                                        name="7-Day Avg", line=dict(color=ACCENT["teal"], width=2)))
        fig_trend.add_trace(go.Scatter(x=fdf["Date"], y=fdf["Rolling14_Load"], mode="lines",
                                        name="14-Day Avg", line=dict(color=ACCENT["orange"], width=2)))
        fig_trend.update_layout(
            template=plotly_template(), margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None, yaxis_title="Children Under Care", height=380,
            legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

with right:
    with panel("CBP vs. HHS Load Split", icon="compare", min_height=560, icon_color=ACCENT["purple"],
               caption="Share of the total system load sitting in each stage of the pipeline."):
        split = pd.DataFrame({
            "Stage": ["CBP Custody", "HHS Care"],
            "Children": [fdf["CBP_Custody"].mean(), fdf["HHS_Care"].mean()],
        })
        fig_split = px.pie(
            split, names="Stage", values="Children", hole=0.6,
            template=plotly_template(), color_discrete_sequence=[ACCENT["orange"], ACCENT["teal"]],
        )
        fig_split.update_traces(textinfo="percent+label")
        fig_split.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                                 paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig_split, use_container_width=True)

        top_strain_day = fdf.loc[fdf["TotalSystemLoad"].idxmax()]
        alert_box(
            f"Peak system load: {top_strain_day['TotalSystemLoad']:,.0f} children",
            f"Recorded on {top_strain_day['Date'].strftime('%B %d, %Y')}."
        )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Net intake / backlog / strain / discharge row
# ---------------------------------------------------------------------------
p1, p2, p3, p4 = st.columns(4)

with p1:
    with panel("Net Daily Intake", icon="power", icon_color=ACCENT["red"]):
        monthly_net = fdf.groupby("MonthLabel", sort=False)["NetDailyIntake"].mean().reset_index()
        fig = px.bar(
            monthly_net.tail(12), x="MonthLabel", y="NetDailyIntake",
            template=plotly_template(), color_discrete_sequence=[ACCENT["red"]],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title=None, yaxis_title="Net Intake/day")
        st.plotly_chart(fig, use_container_width=True)

with p2:
    with panel("Backlog Status Split", icon="anchor", icon_color=ACCENT["teal"]):
        backlog_summary = fdf["BacklogLabel"].value_counts(normalize=True).mul(100).reset_index()
        backlog_summary.columns = ["BacklogLabel", "pct"]
        fig = px.pie(
            backlog_summary, names="BacklogLabel", values="pct", hole=0.6,
            template=plotly_template(), color_discrete_sequence=[ACCENT["red"], ACCENT["teal"]],
        )
        fig.update_traces(textinfo="percent")
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

with p3:
    with panel("Load Level Distribution", icon="shield", icon_color=ACCENT["blue"]):
        level_summary = fdf["LoadLevel"].value_counts().reindex(["Low Load", "Medium Load", "High Load"]).reset_index()
        level_summary.columns = ["LoadLevel", "days"]
        fig = px.bar(
            level_summary, x="LoadLevel", y="days",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title=None, yaxis_title="Reporting Days")
        st.plotly_chart(fig, use_container_width=True)

with p4:
    with panel("Discharges vs. Transfers", icon="user-check", icon_color=ACCENT["green"]):
        monthly_flow = fdf.groupby("MonthLabel", sort=False)[["CBP_Transferred", "HHS_Discharged"]].mean().reset_index().tail(12)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_flow["MonthLabel"], y=monthly_flow["CBP_Transferred"],
                              name="Transferred In", marker_color=ACCENT["orange"]))
        fig.add_trace(go.Bar(x=monthly_flow["MonthLabel"], y=monthly_flow["HHS_Discharged"],
                              name="Discharged", marker_color=ACCENT["green"]))
        fig.update_layout(barmode="group", template=plotly_template(), margin=dict(l=0, r=0, t=0, b=0), height=250,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title=None, yaxis_title="Children/day", legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Strain Overview | Volatility heatmap | Weekday pattern
# ---------------------------------------------------------------------------
h1c, h2c, h3c = st.columns([1.3, 1, 1])

with h1c:
    with panel("Capacity Strain Overview", icon="alert-triangle", icon_color=ACCENT["red"], min_height=400):
        strain_days = fdf[fdf["StrainLabel"] == "Strain"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Strain Days", f"{len(strain_days):,}", f"{len(strain_days)/len(fdf)*100:.1f}% of period")
        m2.metric("Avg. Load on Strain Days", f"{strain_days['TotalSystemLoad'].mean():,.0f}" if len(strain_days) else "0",
                   f"vs {avg_load:,.0f} overall")
        m3.metric("Peak Net Intake", f"{fdf['NetDailyIntake'].max():+.0f}", "single-day high")

        st.markdown("<div class='dash-subtitle' style='font-size:12.5px; margin:6px 0 8px 0;'>Capacity Signal Breakdown</div>",
                    unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        with t1:
            stat_tile("alert-triangle", ACCENT["red"], "Strain Days", f"{len(strain_days):,}", f"{len(strain_days)/len(fdf)*100:.1f}%")
        with t2:
            backlog_building = (fdf["BacklogLabel"] == "Backlog Building").sum()
            stat_tile("anchor", ACCENT["orange"], "Backlog Building", f"{backlog_building:,}", f"{backlog_building/len(fdf)*100:.1f}%")
        with t3:
            high_load_days = (fdf["LoadLevel"] == "High Load").sum()
            stat_tile("shield", ACCENT["purple"], "High Load Days", f"{high_load_days:,}", f"{high_load_days/len(fdf)*100:.1f}%")

with h2c:
    with panel("Load Volatility Heatmap", icon="search", icon_color=ACCENT["orange"], caption="Year × Quarter", min_height=400):
        heat = fdf.groupby(["Year", "Quarter"])["RollingStd7"].mean().reset_index()
        heat_pivot = heat.pivot(index="Year", columns="Quarter", values="RollingStd7")
        fig_heat = px.imshow(
            heat_pivot, text_auto=".0f",
            color_continuous_scale=[ACCENT["blue"], ACCENT["purple"], ACCENT["red"]],
            template=plotly_template(), aspect="auto",
        )
        fig_heat.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                               paper_bgcolor="rgba(0,0,0,0)", height=255, coloraxis_showscale=False)
        st.plotly_chart(fig_heat, use_container_width=True)

with h3c:
    with panel("System Load by Weekday", icon="calendar", icon_color=ACCENT["blue"], min_height=400):
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        wd_summary = fdf.groupby("WeekdayName")["TotalSystemLoad"].mean().reindex(weekday_order).reset_index()
        fig_wd = px.bar(
            wd_summary, x="WeekdayName", y="TotalSystemLoad",
            template=plotly_template(), color_discrete_sequence=[ACCENT["blue"]],
        )
        fig_wd.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             xaxis_title=None, yaxis_title="Avg. System Load", height=275)
        st.plotly_chart(fig_wd, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Key Insights | Recommendations
# ---------------------------------------------------------------------------
year_load = fdf.groupby("Year")["TotalSystemLoad"].mean()
peak_year = year_load.idxmax()
peak_year_load = year_load.max()

quarter_strain = fdf.groupby("Quarter")["StrainLabel"].apply(lambda s: (s == "Strain").mean() * 100)
if len(quarter_strain):
    worst_quarter = quarter_strain.idxmax()
    worst_quarter_rate = quarter_strain.max()
else:
    worst_quarter, worst_quarter_rate = "N/A", 0.0

weekend_load = fdf.loc[fdf["DayType"] == "Weekend", "TotalSystemLoad"].mean()
weekday_load = max(fdf.loc[fdf["DayType"] == "Weekday", "TotalSystemLoad"].mean(), 0.01)
weekend_ratio = weekend_load / weekday_load

i_col, r_col = st.columns(2)

with i_col:
    with panel("Key Insights", icon="bulb", icon_color=ACCENT["orange"], min_height=330):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            insight_tile(f"{peak_year} carried the heaviest load", f"Average total system load in {peak_year} reached {peak_year_load:,.0f} children, the highest of any year in view.",
                       icon="alert-triangle", icon_color=ACCENT["red"])
        with c2:
            insight_tile(f"{worst_quarter} saw the most strain", f"{worst_quarter_rate:.1f}% of reporting days in {worst_quarter} were classified as under strain.",
                       icon="pulse", icon_color=ACCENT["orange"])
        with c3:
            insight_tile("Discharge relief is partial", f"Discharges offset {offset_ratio:.1f}% of transfers into HHS care over the period.",
                       icon="user-check", icon_color=ACCENT["teal"])
        with c4:
            insight_tile("Load volatility is measurable", f"7-day load volatility averages {volatility:.1f}% of mean system load, a useful early-warning signal.",
                       icon="shield", icon_color=ACCENT["purple"])

with r_col:
    with panel("Recommendations", icon="check-circle", icon_color=ACCENT["green"], min_height=330):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            insight_tile(f"Pre-position capacity for {worst_quarter}-like periods", "Use quarter-over-quarter strain rates to plan staffing ahead of historically high-strain windows.",
                       icon="flag", icon_color=ACCENT["green"])
        with c2:
            insight_tile("Strengthen discharge throughput", "Investigate sponsor-vetting bottlenecks to raise the discharge offset ratio and relieve sustained backlog.",
                       icon="user-check", icon_color=ACCENT["blue"])
        with c3:
            insight_tile("Track the volatility index weekly", "A rising 7-day volatility index ahead of a strain period could serve as an early operational alert.",
                       icon="pulse", icon_color=ACCENT["teal"])
        with c4:
            insight_tile("Review weekday staffing patterns", f"Weekend load runs at {weekend_ratio:.2f}x weekday load — align shelter staffing schedules accordingly.",
                       icon="calendar", icon_color=ACCENT["purple"])
