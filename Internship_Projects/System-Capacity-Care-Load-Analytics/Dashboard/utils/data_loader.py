"""
Central data loader for the UAC care-capacity dashboard.

Every page pulls from this module so the derived-metric logic only lives in
one place. If a definition changes (e.g. the strain threshold, or the
rolling window length), this is the only file that needs editing.
"""

import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = "data/UAC_Program_Raw.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [
        "Date",
        "CBP_Intake",
        "CBP_Custody",
        "CBP_Transferred",
        "HHS_Care",
        "HHS_Discharged",
    ]

    # Source numbers arrive as strings with thousands separators (e.g. "2,484")
    for col in ["CBP_Intake", "CBP_Custody", "CBP_Transferred", "HHS_Care", "HHS_Discharged"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    df[["CBP_Intake", "CBP_Custody", "CBP_Transferred", "HHS_Care", "HHS_Discharged"]] = df[
        ["CBP_Intake", "CBP_Custody", "CBP_Transferred", "HHS_Care", "HHS_Discharged"]
    ].ffill()

    # --- Derived healthcare capacity metrics -------------------------------
    df["TotalSystemLoad"] = df["CBP_Custody"] + df["HHS_Care"]
    df["NetDailyIntake"] = df["CBP_Transferred"] - df["HHS_Discharged"]
    df["CareLoadGrowthRate"] = df["TotalSystemLoad"].pct_change() * 100
    df["CareLoadGrowthRate"] = df["CareLoadGrowthRate"].replace([np.inf, -np.inf], np.nan)

    # Rolling windows (computed on calendar order, not fixed-cadence days —
    # the source is reported on an irregular schedule)
    df["Rolling7_Load"] = df["TotalSystemLoad"].rolling(7, min_periods=1).mean()
    df["Rolling14_Load"] = df["TotalSystemLoad"].rolling(14, min_periods=1).mean()
    df["RollingStd7"] = df["TotalSystemLoad"].rolling(7, min_periods=2).std()

    # Backlog indicator: sustained positive net intake (trailing 14-report window)
    df["Backlog14"] = df["NetDailyIntake"].rolling(14, min_periods=1).sum()
    df["BacklogLabel"] = np.where(df["Backlog14"] > 0, "Backlog Building", "Backlog Relieving")

    # Discharge offset ratio: how much of what moves into HHS gets relieved
    # back out via discharge, on the same report
    df["DischargeOffsetRatio"] = (df["HHS_Discharged"] / df["CBP_Transferred"].replace(0, np.nan)) * 100
    df["DischargeOffsetRatio"] = df["DischargeOffsetRatio"].clip(upper=300)

    # Strain vs relief: total load meaningfully above its own trailing mean
    roll_mean_30 = df["TotalSystemLoad"].rolling(30, min_periods=5).mean()
    roll_std_30 = df["TotalSystemLoad"].rolling(30, min_periods=5).std()
    df["StrainLabel"] = np.where(
        df["TotalSystemLoad"] > (roll_mean_30 + roll_std_30), "Strain", "Normal/Relief"
    )
    df.loc[roll_mean_30.isna(), "StrainLabel"] = "Normal/Relief"

    # Load level bands (Low / Medium / High) — analogous to a credit-score band
    df["LoadLevel"] = pd.qcut(
        df["TotalSystemLoad"], q=[0, 0.33, 0.66, 1.0],
        labels=["Low Load", "Medium Load", "High Load"],
    )

    # Calendar segmentation fields
    df["Year"] = df["Date"].dt.year
    df["Quarter"] = "Q" + df["Date"].dt.quarter.astype(str) + " " + df["Year"].astype(str)
    df["MonthLabel"] = df["Date"].dt.strftime("%b %Y")
    df["MonthNum"] = df["Date"].dt.to_period("M")
    df["WeekdayName"] = df["Date"].dt.day_name()
    df["DayType"] = np.where(df["Date"].dt.dayofweek >= 5, "Weekend", "Weekday")

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """filters: dict of {column_name: selected_value_or_'All'}."""
    out = df.copy()
    for col, val in filters.items():
        if val and val != "All":
            out = out[out[col] == val]
    return out


def apply_date_range(df: pd.DataFrame, start, end) -> pd.DataFrame:
    if start is None or end is None:
        return df
    return df[(df["Date"] >= pd.Timestamp(start)) & (df["Date"] <= pd.Timestamp(end))]


def net_intake_pressure(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return df["NetDailyIntake"].mean()


def care_load_volatility(df: pd.DataFrame) -> float:
    """Volatility index: rolling-7 std as a % of mean total system load."""
    if len(df) == 0 or df["TotalSystemLoad"].mean() == 0:
        return 0.0
    return (df["RollingStd7"].mean() / df["TotalSystemLoad"].mean()) * 100


def discharge_offset_ratio(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    total_transferred = df["CBP_Transferred"].sum()
    if total_transferred == 0:
        return 0.0
    return (df["HHS_Discharged"].sum() / total_transferred) * 100


def backlog_accumulation_rate(df: pd.DataFrame) -> float:
    """Average day-over-day change in the 14-report backlog indicator."""
    if len(df) < 2:
        return 0.0
    return df["Backlog14"].diff().mean()


def strain_share(df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return (df["StrainLabel"] == "Strain").mean() * 100
