"""
Central data loader for the churn dashboard.

Every page pulls from this module so the segmentation logic only lives in
one place. If the banding definitions change (e.g. credit score cutoffs),
this is the only file that needs editing.
"""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Churn_Modelling.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)

    # The source CSV has no customer identifier column at all (it was
    # stripped from the standard Kaggle churn dataset before landing here).
    # Several pages (Customer Table, High Value Explorer) need something to
    # key/search rows by, so we synthesize a stable one from the row index.
    if "CustomerId" not in df.columns:
        df.insert(0, "CustomerId", 10001 + df.index)

    # --- Age band --------------------------------------------------------
    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 30, 45, 60, 200],
        labels=["<30", "30-45", "46-60", "60+"],
        right=True,
    )

    # --- Credit score band -------------------------------------------------
    df["CreditScoreBand"] = pd.cut(
        df["CreditScore"],
        bins=[0, 450, 650, 900],
        labels=["Low (<450)", "Medium (450-650)", "High (>650)"],
    )

    # Finer bands purely for the credit-score-band chart on Overview,
    # matches the reference dashboard's 6-bucket breakdown
    df["CreditScoreBandFine"] = pd.cut(
        df["CreditScore"],
        bins=[0, 450, 550, 650, 750, 850, 1000],
        labels=["300-450", "451-550", "551-650", "651-750", "751-850", "851-900"],
    )

    # --- Tenure group --------------------------------------------------
    df["TenureGroup"] = pd.cut(
        df["Tenure"],
        bins=[-1, 0, 5, 100],
        labels=["New (<1Y)", "Mid (1-5Y)", "Long-Term (>5Y)"],
    )

    # --- Balance segment --------------------------------------------------
    def balance_segment(bal):
        if bal == 0:
            return "Zero Balance"
        elif bal < 100_000:
            return "Low Balance"
        else:
            return "High Balance"

    df["BalanceSegment"] = df["Balance"].apply(balance_segment)

    # --- Activity label for readability -------------------------------
    df["ActivityStatus"] = df["IsActiveMember"].map({1: "Active", 0: "Inactive"})
    df["ChurnLabel"] = df["Exited"].map({1: "Churned", 0: "Retained"})

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    filters: dict of {column_name: selected_value_or_'All'}
    Central place so every page filters identically.
    """
    out = df.copy()
    for col, val in filters.items():
        if val and val != "All":
            out = out[out[col] == val]
    return out


def churn_rate(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return df["Exited"].mean() * 100


# ---------------------------------------------------------------------------
# The source CSV is a single-period snapshot — there is no transaction date
# column, so there is no real "month over month" churn trend in the data.
# The reference design calls for a trend line, so this builds an
# illustrative 5-point series that lands on the *real* overall churn rate
# for the current filter selection. It's deterministic (same filters ->
# same shape) rather than randomized, and every page that uses it should
# label it clearly as illustrative.
# ---------------------------------------------------------------------------
def simulate_monthly_trend(df: pd.DataFrame, months=None):
    import numpy as np

    if months is None:
        months = ["Jan 2025", "Feb 2025", "Mar 2025", "Apr 2025", "May 2025"]

    end_rate = churn_rate(df)
    start_rate = max(end_rate - 1.7, 0.0)
    base = np.linspace(start_rate, end_rate, len(months))
    wiggle = np.array([0.0, 0.35, -0.25, 0.3, 0.0])[: len(months)]
    values = np.clip(base + wiggle, 0, 100)
    values[-1] = end_rate  # last point always ties out to the real number

    total_churned = int((df["Exited"] == 1).sum())
    churned_counts = np.round(np.linspace(total_churned * 0.75, total_churned, len(months))).astype(int)

    return pd.DataFrame({"Month": months, "ChurnRate": values, "ChurnedCustomers": churned_counts})


def high_value_segments(df: pd.DataFrame, balance_q: float = 0.75, salary_q: float = 0.75) -> dict:
    """High Balance / High Salary / Premium (both) counts, for the segmentation tiles."""
    if len(df) == 0:
        return {"high_balance": (0, 0.0), "high_salary": (0, 0.0), "premium": (0, 0.0)}

    bal_cut = df["Balance"].quantile(balance_q)
    sal_cut = df["EstimatedSalary"].quantile(salary_q)
    is_high_bal = df["Balance"] >= bal_cut
    is_high_sal = df["EstimatedSalary"] >= sal_cut

    n = len(df)
    hb = int(is_high_bal.sum())
    hs = int(is_high_sal.sum())
    prem = int((is_high_bal & is_high_sal).sum())

    return {
        "high_balance": (hb, hb / n * 100),
        "high_salary": (hs, hs / n * 100),
        "premium": (prem, prem / n * 100),
    }