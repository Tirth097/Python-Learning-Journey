import streamlit as st

from utils.data_loader import (
    load_data, apply_filters, discharge_offset_ratio, care_load_volatility, strain_share,
)
from utils.styling import inject_theme, ACCENT, panel

inject_theme()
df = load_data()

st.markdown("<h2>Key Insights &amp; Recommendations</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle'>Generated from the current data — re-run after each refresh, these numbers move with the file.</p>",
    unsafe_allow_html=True,
)

year_filter = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
fdf = apply_filters(df, {"Year": year_filter})

# ---------------------------------------------------------------------------
# Derive the findings from the data rather than hardcoding them, so this
# page stays accurate if the underlying file changes.
# ---------------------------------------------------------------------------
year_load = fdf.groupby("Year")["TotalSystemLoad"].mean()
peak_year = year_load.idxmax()
peak_year_load = year_load.max()

quarter_strain = fdf.groupby("Quarter")["StrainLabel"].apply(lambda s: (s == "Strain").mean() * 100)
worst_quarter = quarter_strain.idxmax() if len(quarter_strain) else "N/A"
worst_quarter_rate = quarter_strain.max() if len(quarter_strain) else 0.0

offset_ratio = discharge_offset_ratio(fdf)
volatility = care_load_volatility(fdf)
strain_pct = strain_share(fdf)

backlog_building_pct = (fdf["BacklogLabel"] == "Backlog Building").mean() * 100

# ---------------------------------------------------------------------------
# Insight cards
# ---------------------------------------------------------------------------
st.markdown('<div class="panel-title" style="font-size:18px; margin-bottom:14px;">Key Insights</div>', unsafe_allow_html=True)

i1, i2 = st.columns(2)
with i1:
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['red']};">
            <b style="color:#f8fafc;">{peak_year} carried the heaviest system load</b><br>
            <span style="color:#94a3b8;">
            Average total system load in {peak_year} reached <b>{peak_year_load:,.0f}</b> children,
            the highest of any year in the filtered view.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['orange']};">
            <b style="color:#f8fafc;">{worst_quarter} shows the highest strain rate</b><br>
            <span style="color:#94a3b8;">
            <b>{worst_quarter_rate:.1f}%</b> of reporting days in {worst_quarter} were flagged as
            under strain — the steepest of any quarter, worth targeting for advance staffing.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with i2:
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['teal']};">
            <b style="color:#f8fafc;">Discharge throughput only partially offsets intake</b><br>
            <span style="color:#94a3b8;">
            Discharges cover roughly <b>{offset_ratio:.1f}%</b> of transfers into HHS care —
            sponsor placement capacity is a real constraint on relieving system load.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card" style="border-left: 4px solid {ACCENT['purple']};">
            <b style="color:#f8fafc;">Load volatility is a leading strain signal</b><br>
            <span style="color:#94a3b8;">
            The system runs at roughly <b>{strain_pct:.1f}%</b> of reporting days under strain, with
            7-day load volatility averaging <b>{volatility:.1f}%</b> of mean system load —
            a signal that tends to rise ahead of strain windows.
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
            <b style="color:#f8fafc;">Pre-position staffing ahead of {worst_quarter}-like windows</b><br>
            <span style="color:#94a3b8;">
            Given the {worst_quarter_rate:.1f}% strain rate, scheduling surge staffing and shelter
            capacity ahead of historically high-strain quarters would blunt the next spike.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Address the sponsor-placement bottleneck</b><br>
            <span style="color:#94a3b8;">
            With discharges offsetting only {offset_ratio:.1f}% of HHS transfers, streamlining
            sponsor vetting could meaningfully reduce sustained backlog accumulation.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with r2:
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Stand up a volatility-based early warning trigger</b><br>
            <span style="color:#94a3b8;">
            Since load volatility tends to climb before strain periods, a rolling 7-day volatility
            alert (at {volatility:.1f}% average) could give planners a few days' lead time.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card">
            <b style="color:#f8fafc;">Monitor {peak_year}-scale years for recurrence</b><br>
            <span style="color:#94a3b8;">
            Average load of {peak_year_load:,.0f} children in {peak_year} should serve as the
            planning ceiling when budgeting shelter and medical staffing for future years.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    f"Backlog was building on {backlog_building_pct:.1f}% of reporting days in the current view. "
    "These insights are computed live from the loaded CSV."
)
