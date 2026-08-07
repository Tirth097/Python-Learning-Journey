import streamlit as st

from utils.data_loader import load_data, apply_filters
from utils.styling import inject_theme, kpi_card, panel


inject_theme()
df = load_data()

st.markdown("<h2 class='' >Customer Table</h2>", unsafe_allow_html=True)
st.markdown(
    "<p class='dash-subtitle' >Row-level view for exporting or spot-checking specific customers.</p>",
    unsafe_allow_html=True,
)

st.sidebar.subheader("Filters")
geo_filter = st.sidebar.selectbox("Geography", ["All"] + sorted(df["Geography"].unique().tolist()))
gender_filter = st.sidebar.selectbox("Gender", ["All"] + sorted(df["Gender"].unique().tolist()))
churn_filter = st.sidebar.selectbox("Status", ["All", "Churned", "Retained"])
active_filter = st.sidebar.selectbox("Activity", ["All", "Active", "Inactive"])

fdf = apply_filters(df, {"Geography": geo_filter, "Gender": gender_filter})
if churn_filter != "All":
    fdf = fdf[fdf["ChurnLabel"] == churn_filter]
if active_filter != "All":
    fdf = fdf[fdf["ActivityStatus"] == active_filter]

search_id = st.sidebar.text_input("Search Customer ID")
if search_id:
    fdf = fdf[fdf["CustomerId"].astype(str).str.contains(search_id)]

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Rows in View", f"{len(fdf):,}")
with k2:
    kpi_card("Churned in View", f"{(fdf['Exited'] == 1).sum():,}")
with k3:
    kpi_card("Avg. Balance in View", f"€{fdf['Balance'].mean():,.0f}" if len(fdf) else "€0")

st.markdown("<br>", unsafe_allow_html=True)

display_cols = [
    "CustomerId", "Geography", "Gender", "Age", "CreditScore", "Tenure",
    "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
    "EstimatedSalary", "ChurnLabel",
]
with panel("Customer Table", icon="users"):
    st.dataframe(fdf[display_cols], hide_index=True, use_container_width=True, height=520)

st.download_button(
    "Download filtered data as CSV",
    data=fdf[display_cols].to_csv(index=False).encode("utf-8"),
    file_name="filtered_customers.csv",
    mime="text/csv",
)