import streamlit as st

from utils.data_loader import load_data, apply_filters, apply_date_range
from utils.styling import inject_theme, kpi_card, panel

inject_theme()
df = load_data()

st.markdown("<h2>Daily Records Table</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle'>Row-level view for exporting or spot-checking specific reporting days.</p>",
    unsafe_allow_html=True,
)

st.sidebar.subheader("Filters")
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
year_filter = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist(), reverse=True))
strain_filter = st.sidebar.selectbox("System Status", ["All", "Strain", "Normal/Relief"])
backlog_filter = st.sidebar.selectbox("Backlog Status", ["All", "Backlog Building", "Backlog Relieving"])

fdf = apply_filters(df, {"Year": year_filter})
if isinstance(date_range, tuple) and len(date_range) == 2:
    fdf = apply_date_range(fdf, date_range[0], date_range[1])
if strain_filter != "All":
    fdf = fdf[fdf["StrainLabel"] == strain_filter]
if backlog_filter != "All":
    fdf = fdf[fdf["BacklogLabel"] == backlog_filter]

search_date = st.sidebar.text_input("Search Date (e.g. 2025-06)")
if search_date:
    fdf = fdf[fdf["Date"].astype(str).str.contains(search_date)]

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Rows in View", f"{len(fdf):,}")
with k2:
    kpi_card("Strain Days in View", f"{(fdf['StrainLabel'] == 'Strain').sum():,}")
with k3:
    kpi_card("Avg. System Load in View", f"{fdf['TotalSystemLoad'].mean():,.0f}" if len(fdf) else "0")

st.markdown("<br>", unsafe_allow_html=True)

display_cols = [
    "Date", "CBP_Intake", "CBP_Custody", "CBP_Transferred", "HHS_Care", "HHS_Discharged",
    "TotalSystemLoad", "NetDailyIntake", "LoadLevel", "StrainLabel", "BacklogLabel",
]
with panel("Daily Records", icon="calendar"):
    st.dataframe(fdf[display_cols], hide_index=True, use_container_width=True, height=520)

st.download_button(
    "Download filtered data as CSV",
    data=fdf[display_cols].to_csv(index=False).encode("utf-8"),
    file_name="filtered_uac_records.csv",
    mime="text/csv",
)
