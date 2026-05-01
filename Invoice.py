# Invoice.py

# Invoice generation for the Freelance Time and Pay Tracker.

import datetime
from tkinter import filedialog, messagebox

import numpy as np

from Pandas import get_client_sessions_for_invoice

# ====================
# Build invoice text
# ====================


def build_invoice_text(client_name, client_df):

    # Build a plaintext invoice for the given client using their session data.
    # The invoice includes client name, date issued, hourly rate, a table of sessions with date, hours, earnings,
    # and description, and a total amount due.

    today = datetime.date.today().strftime("%Y-%m-%d")

    if client_df.empty:
        return f"No sessions found for client: {client_name}"

    hourly_rate = client_df["hourly_rate"].iloc[0]

    lines = []
    lines.append("=" * 60)
    lines.append("INVOICE")
    lines.append("=" * 60)
    lines.append(f"Client:       {client_name}")
    lines.append(f"Date Issued:  {today}")
    lines.append(f"Hourly Rate:  ${np.round(hourly_rate, 2):.2f}")
    lines.append("-" * 60)
    lines.append(f"{'Date':<12}  {'Hours':>6}  {'Earned':>10}  Description")
    lines.append("-" * 60)

    total_hours = 0.0
    total_earned = 0.0

    for _, row in client_df.iterrows():
        date = row["date"]
        hours = row["hours"]
        earned = np.round(hours * hourly_rate, 2)
        desc = row["description"] if row["description"] else ""
        lines.append(f"{date:<12}  {hours:>6.2f}  ${earned:>9.2f}  {desc}")
        total_hours += hours
        total_earned += earned

    lines.append("-" * 60)
    lines.append(
        f"{'TOTAL':>12}  {np.round(total_hours, 2):>6.2f}  ${np.round(total_earned, 2):>9.2f}"
    )
    lines.append("=" * 60)
    lines.append(f"AMOUNT DUE: ${np.round(total_earned, 2):.2f}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ==============================
# Save invoice via file dialog
# ==============================


def save_invoice(client_name):

    # Get the client's sessions to include in the invoice

    client_df = get_client_sessions_for_invoice(client_name)

    if client_df.empty:
        messagebox.showwarning("No Data", f"No sessions found for '{client_name}'.")
        return

    invoice_text = build_invoice_text(client_name, client_df)

    # Open OS file picker (spec item t)
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        initialfile=f"invoice_{client_name.replace(' ', '_')}_{datetime.date.today()}.txt",
        title="Save Invoice",
    )

    # Spec item v: check for empty path before writing — must not crash on Cancel
    if not path:
        return  # user cancelled, do nothing

    with open(path, "w") as f:
        f.write(invoice_text)

    messagebox.showinfo("Invoice Saved", f"Invoice saved to:\n{path}")
