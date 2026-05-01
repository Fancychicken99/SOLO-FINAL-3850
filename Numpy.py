# Numpy.py

# All numpy operations for the Freelance Time and Pay Tracker.

import numpy as np

# =======================
# Core Numpy Operations
# =======================


def total_hours(hours_series):
    # return the total hours from a pandas Series of hours using numpy sum.
    return float(np.round(np.sum(hours_series.to_numpy()), 2))


def average_session_earnings(earnings_series):
    # return the average session earnings from a pandas Series of earnings using numpy mean.
    return float(np.round(np.mean(earnings_series.to_numpy()), 2))


def round_currency(value):
    # Round a numeric value to 2 decimal places for currency display.
    return np.round(value, 2)


def round_currency_series(series):
    # Round a pandas Series of numeric values to 2 decimal places for currency display.
    return np.round(series.to_numpy(), 2)


# ===============================================
# Summary Stats Block Called by Pay Summary Tab
# ===============================================


def compute_summary_stats(df):

    # Given a DataFrame with 'hours' and 'earnings' columns, compute total hours, average session earnings, 
    # and grand total earned using numpy operations.

    # If the DataFrame is empty, return zeros for all summary stats to avoid NaN issues.
    if df.empty:
        return {
            "total_hours": 0.0,
            "avg_session_earnings": 0.0,
            "grand_total_earned": 0.0,
        }

    # np.sum on hours array (spec item o)
    total_hrs = float(np.round(np.sum(df["hours"].to_numpy()), 2))

    # np.mean on earnings array (spec item o)
    avg_earn = float(np.round(np.mean(df["earnings"].to_numpy()), 2))

    # np.sum on earnings, then np.round for currency display (spec item o)
    grand_total = float(np.round(np.sum(df["earnings"].to_numpy()), 2))

    # Return a dictionary of the computed summary stats.
    return {
        "total_hours": total_hrs,
        "avg_session_earnings": avg_earn,
        "grand_total_earned": grand_total,
    }


def apply_rounding_to_summary(summary_df):

    # Round the total_hours, total_earned, and avg_session_earnings columns to 2 decimal places for currency display.
    summary_df = summary_df.copy()
    summary_df["total_hours"] = np.round(summary_df["total_hours"].to_numpy(), 2)
    summary_df["total_earned"] = np.round(summary_df["total_earned"].to_numpy(), 2)
    summary_df["avg_session_earnings"] = np.round(
        summary_df["avg_session_earnings"].to_numpy(), 2
    )
    return summary_df
