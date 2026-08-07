import streamlit as st

from utils.styling import inject_theme, sidebar_brand, sidebar_footer

st.set_page_config(page_title="EuroBank Analytics", layout="wide", initial_sidebar_state="expanded")

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

inject_theme()
sidebar_brand()

pages = [
    st.Page("pages/0_Overview.py", title="Overview", icon=":material/space_dashboard:", default=True),
    st.Page("pages/1_Geography.py", title="Geography Analysis", icon=":material/globe:"),
    st.Page("pages/2_Age_and_Tenure.py", title="Age & Tenure Analysis", icon=":material/analytics:"),
    st.Page("pages/3_High_Value_explorer.py", title="High Value Explorer", icon=":material/diamond:"),
    st.Page("pages/4_Customer_Segmentation.py", title="Customer Segmentation", icon=":material/group:"),
    st.Page("pages/5_Customer_Table.py", title="Customer Table", icon=":material/table_rows:"),
    st.Page("pages/6_Insights_Recommendations.py", title="Insights & Recommendations", icon=":material/tips_and_updates:"),
]

nav = st.navigation(pages)
nav.run()

sidebar_footer()