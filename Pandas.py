# Pandas.py

# All pandas operations for the Freelance Time and Pay Tracker.

import pandas as pd
import Numpy as np
import sqlite3

from Database import DB_PATH, get_connection

# ===============================================
# Load Data from SQlite into a Pandas DataFrame
# ===============================================


def load_sessions_dataframe():

    # Load all sessions joined with client data into a DataFrame, calculate earnings, and return the DataFrame.
    # This will be called by the Sessions tab to load session data and by the Pay Summary tab to build the summary.
    conn = get_connection()

    query = """
        SELECT
            s.id          AS session_id,
            c.name        AS client_name,
            c.hourly_rate,
            s.date,
            s.hours,
            COALESCE(s.description, '') AS description
        FROM sessions s
        JOIN clients c ON s.client_id = c.id
        ORDER BY s.date DESC
    """

    # pd.read_sql() is the required way to load data (spec item l)
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        # Return a properly-shaped empty DataFrame so callers don't crash
        return pd.DataFrame(
            columns=[
                "session_id",
                "client_name",
                "hourly_rate",
                "date",
                "hours",
                "description",
                "earnings",
            ]
        )

    # Calculated column — never stored in the DB (spec item m)
    df["earnings"] = df["hours"] * df["hourly_rate"]

    return df


# ==================================
# Per-client summary using groupby
# ==================================


def build_summary(df):
    # Given a DataFrame of sessions, build a summary DataFrame grouped by client with total hours, total earned, and average session earnings.
    # This will be called by the Pay Summary tab to build the summary table.
    if df.empty:
        return pd.DataFrame(
            columns=[
                "client_name",
                "sessions",
                "total_hours",
                "total_earned",
                "avg_session_earnings",
            ]
        )

    # groupby per client, aggregate sessions count, total hours, total earned
    summary = (
        df.groupby("client_name")
        .agg(
            sessions=("session_id", "count"),
            total_hours=("hours", "sum"),
            total_earned=("earnings", "sum"),
        )
        .reset_index()
    )

    # Average earnings per session — will be rounded via np.round in numpy_ops
    summary["avg_session_earnings"] = summary["total_earned"] / summary["sessions"]

    return summary


# ============
# CSV export
# ============


def export_summary_to_csv(summary_df, path):
    # Export the summary DataFrame to a CSV file at the specified path. This will be called by the Pay Summary tab's export button.
    summary_df.to_csv(path, index=False)


# =====================
# Invoice data helper
# =====================


def get_client_sessions_for_invoice(client_name):
    # Load all sessions into a DataFrame, then filter to just the sessions for the specified client.
    # This will be used to build the invoice data.
    df = load_sessions_dataframe()
    if df.empty:
        return df
    return df[df["client_name"] == client_name].copy()
