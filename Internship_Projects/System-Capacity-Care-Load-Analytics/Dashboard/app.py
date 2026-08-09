import streamlit as st

from utils.styling import inject_theme, sidebar_brand, sidebar_footer

st.set_page_config(page_title="UAC Care Capacity Analytics", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

inject_theme()
sidebar_brand()

pages = [
    st.Page("pages/0_Overview.py", title="System Load Overview", icon=":material/space_dashboard:", default=True),
    st.Page("pages/1_CBP_vs_HHS.py", title="CBP vs HHS Comparison", icon=":material/compare_arrows:"),
    st.Page("pages/2_Trends_and_Volatility.py", title="Trends & Volatility", icon=":material/analytics:"),
    st.Page("pages/3_Capacity_Stress_Explorer.py", title="Capacity Stress Explorer", icon=":material/emergency:"),
    st.Page("pages/4_Period_Segmentation.py", title="Period Segmentation", icon=":material/calendar_view_month:"),
    st.Page("pages/5_Daily_Records_Table.py", title="Daily Records Table", icon=":material/table_rows:"),
    st.Page("pages/6_Insights_Recommendations.py", title="Insights & Recommendations", icon=":material/tips_and_updates:"),
]

nav = st.navigation(pages)
nav.run()

sidebar_footer()
