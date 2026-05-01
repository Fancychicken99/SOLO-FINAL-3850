# GUI.py

# All tkinter GUI code for the Freelance Time and Pay Tracker.

# Organized into tab functions:

# Tabs:

# Clients Tab
# Sessions Tab
# Pay Summary Tab
# Invoice Tab

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import datetime

import Database as db
import Pandas as po
import Numpy as no
import Invoice as inv

# =================
# Helper Functions
# =================


def validate_date(dateStr):
    # Return true if dateStr is in correct format and is a valid calendar date, else false
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dateStr):
        # Quick regex check for format YYYY-MM-DD
        return False
    try:
        datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        # This will raise ValueError if the date is invalid
        return True
    except ValueError:
        # If the date is not valid return False
        return False


def validate_hours(hoursStr):
    # Return true if hoursStr is a positive number, else false
    try:
        hours = float(hoursStr)
        if hours <= 0:
            return False, None
        return True, hours
    except ValueError:
        return False, None


# =========== Clients Tab ===========


def build_clients_tab(notebook):
    # Build the Clients tab and attach it to the notebook.

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Clients")

    # ==== Add Client form ====
    form_frame = ttk.LabelFrame(frame, text="Add New Client", padding=10)
    form_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(form_frame, text="Client Name *").grid(
        row=0, column=0, sticky="w", pady=3
    )
    name_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, padx=5)

    ttk.Label(form_frame, text="Hourly Rate ($) *").grid(
        row=1, column=0, sticky="w", pady=3
    )
    rate_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=rate_var, width=30).grid(row=1, column=1, padx=5)

    ttk.Label(form_frame, text="Contact (optional)").grid(
        row=2, column=0, sticky="w", pady=3
    )
    contact_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=contact_var, width=30).grid(
        row=2, column=1, padx=5
    )

    # ==== Clients Treeview ====
    tree_frame = ttk.LabelFrame(frame, text="All Clients", padding=10)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("name", "rate", "contact", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
    tree.heading("name", text="Client Name")
    tree.heading("rate", text="Hourly Rate")
    tree.heading("contact", text="Contact")
    tree.heading("status", text="Status")
    tree.column("name", width=180)
    tree.column("rate", width=100, anchor="e")
    tree.column("contact", width=160)
    tree.column("status", width=80, anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ==== Refresh function — call after every add/archive ====
    # Stored in a list so the closure can be shared with session tab refresh
    _session_refresh_callbacks = []

    def refresh_clients():
        # Clear and repopulate the clients Treeview from the database.
        for row in tree.get_children():
            tree.delete(row)
        for c in db.get_clients():
            status = "Active" if c["active"] else "Archived"
            tree.insert(
                "",
                "end",
                iid=str(c["id"]),
                values=(
                    c["name"],
                    f"${c['hourly_rate']:.2f}",
                    c["contact"] or "",
                    status,
                ),
            )
        # Also tell the sessions tab to refresh its dropdown
        for cb in _session_refresh_callbacks:
            cb()

    def add_client():
        name = name_var.get().strip()
        rate_str = rate_var.get().strip()
        contact = contact_var.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Client name is required.")
            return
        try:
            rate = float(rate_str)
            if rate < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Validation Error", "Hourly rate must be a non-negative number."
            )
            return

        try:
            db.add_client(name, rate, contact)
            name_var.set("")
            rate_var.set("")
            contact_var.set("")
            refresh_clients()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    ttk.Button(form_frame, text="Add Client", command=add_client).grid(
        row=3, column=1, sticky="e", pady=8
    )

    # Initial load
    refresh_clients()

    # Return the callback list so other tabs can register their dropdown refresh
    return _session_refresh_callbacks


# ============= Sessions Tab =============


def build_sessions_tab(notebook, client_refresh_callbacks):
    # Build the Sessions tab.
  
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Log Session")

    # ==== Log Session form ====
    form_frame = ttk.LabelFrame(frame, text="Log Work Session", padding=10)
    form_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(form_frame, text="Client *").grid(row=0, column=0, sticky="w", pady=3)
    client_var = tk.StringVar()
    client_dropdown = ttk.Combobox(
        form_frame, textvariable=client_var, state="readonly", width=28
    )
    client_dropdown.grid(row=0, column=1, padx=5)

    ttk.Label(form_frame, text="Date (YYYY-MM-DD) *").grid(
        row=1, column=0, sticky="w", pady=3
    )
    date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
    ttk.Entry(form_frame, textvariable=date_var, width=30).grid(row=1, column=1, padx=5)

    ttk.Label(form_frame, text="Hours Worked *").grid(
        row=2, column=0, sticky="w", pady=3
    )
    hours_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=hours_var, width=30).grid(
        row=2, column=1, padx=5
    )

    ttk.Label(form_frame, text="Description").grid(row=3, column=0, sticky="w", pady=3)
    desc_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=desc_var, width=30).grid(row=3, column=1, padx=5)

    # ==== Filter bar ====
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill="x", padx=10, pady=2)
    ttk.Label(filter_frame, text="Filter by Client:").pack(side="left")
    filter_var = tk.StringVar(value="All Clients")
    filter_dropdown = ttk.Combobox(
        filter_frame, textvariable=filter_var, state="readonly", width=25
    )
    filter_dropdown.pack(side="left", padx=5)

    # ==== Sessions Treeview ====
    tree_frame = ttk.LabelFrame(frame, text="Work Sessions", padding=10)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("date", "client", "hours", "earnings", "description")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
    tree.heading("date", text="Date")
    tree.heading("client", text="Client")
    tree.heading("hours", text="Hours")
    tree.heading("earnings", text="Earnings")
    tree.heading("description", text="Description")
    tree.column("date", width=100)
    tree.column("client", width=150)
    tree.column("hours", width=70, anchor="e")
    tree.column("earnings", width=90, anchor="e")
    tree.column("description", width=220)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mapping: display name -> client_id (populated by refresh_dropdown)
    _client_map = {}

    def refresh_dropdown():
        # Pull active clients live from the database.
        # Never use a hardcoded list.
        clients = db.get_active_clients()
        _client_map.clear()
        names = []
        for c in clients:
            _client_map[c["name"]] = c["id"]
            names.append(c["name"])
        client_dropdown["values"] = names
        filter_dropdown["values"] = ["All Clients"] + names

    def refresh_sessions():
        # Clear and repopulate the sessions Treeview.
        for row in tree.get_children():
            tree.delete(row)
        selected = filter_var.get()
        cid = _client_map.get(selected) if selected != "All Clients" else None
        for s in db.get_sessions(client_id=cid):
            tree.insert(
                "",
                "end",
                iid=str(s["id"]),
                values=(
                    s["date"],
                    s["client_name"],
                    f"{s['hours']:.2f}",
                    f"${s['earnings']:.2f}",  # earnings calculated in DB query, not stored
                    s["description"] or "",
                ),
            )

    def add_session():
        client_name = client_var.get().strip()
        date_str = date_var.get().strip()
        hours_str = hours_var.get().strip()
        desc = desc_var.get().strip()

        if not client_name:
            messagebox.showerror("Validation Error", "Please select a client.")
            return

        # Validate date format
        if not validate_date(date_str):
            messagebox.showerror(
                "Validation Error",
                "Date must be in YYYY-MM-DD format (e.g. 2025-06-15).",
            )
            return

        # Validate hours as positive number
        ok, hours = validate_hours(hours_str)
        if not ok:
            messagebox.showerror(
                "Validation Error",
                "Hours must be a positive number (e.g. 1.5). Zero or negative values are not allowed.",
            )
            return

        client_id = _client_map[client_name]
        db.add_session(client_id, date_str, hours, desc)

        hours_var.set("")
        desc_var.set("")

        # Refresh immediately after add
        refresh_sessions()

    def delete_session():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a session to delete.")
            return
        # Confirmation prompt before delete
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected session? This cannot be undone.",
        )
        if confirmed:
            session_id = int(selected[0])
            db.delete_session(session_id)
            refresh_sessions()

    def on_filter_change(event=None):
        refresh_sessions()

    filter_dropdown.bind("<<ComboboxSelected>>", on_filter_change)

    ttk.Button(form_frame, text="Log Session", command=add_session).grid(
        row=4, column=1, sticky="e", pady=8
    )

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", padx=10, pady=2)
    ttk.Button(btn_frame, text="Delete Selected Session", command=delete_session).pack(
        side="right"
    )

    # Register refresh_dropdown so Clients tab can call it after adding a client
    client_refresh_callbacks.append(refresh_dropdown)

    refresh_dropdown()
    refresh_sessions()

    # Return refresh_sessions so Pay Summary tab can call it
    return refresh_sessions


# ========== Pay Summary Tab ==========


def build_summary_tab(notebook):
    # Build the Pay Summary tab.

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Pay Summary")

    # ==== Stats bar ====
    stats_frame = ttk.LabelFrame(frame, text="Overall Stats (NumPy)", padding=10)
    stats_frame.pack(fill="x", padx=10, pady=10)

    total_hours_lbl = ttk.Label(stats_frame, text="Total Hours: —")
    total_hours_lbl.grid(row=0, column=0, padx=20)
    avg_earn_lbl = ttk.Label(stats_frame, text="Avg Session Earnings: —")
    avg_earn_lbl.grid(row=0, column=1, padx=20)
    grand_total_lbl = ttk.Label(stats_frame, text="Grand Total Earned: —")
    grand_total_lbl.grid(row=0, column=2, padx=20)

    # ==== Summary Treeview (per-client) ====
    tree_frame = ttk.LabelFrame(
        frame, text="Per-Client Summary (Pandas groupby)", padding=10
    )
    tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("client", "sessions", "total_hours", "total_earned", "avg_earned")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    tree.heading("client", text="Client")
    tree.heading("sessions", text="Sessions")
    tree.heading("total_hours", text="Total Hours")
    tree.heading("total_earned", text="Total Earned")
    tree.heading("avg_earned", text="Avg / Session")
    tree.column("client", width=180)
    tree.column("sessions", width=80, anchor="center")
    tree.column("total_hours", width=100, anchor="e")
    tree.column("total_earned", width=110, anchor="e")
    tree.column("avg_earned", width=110, anchor="e")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Keep a reference to the current summary DataFrame for invoice + CSV
    _state = {"summary_df": None, "full_df": None}

    def refresh_summary():
        # Reload all data via Pandas (pd.read_sql + groupby) and NumPy stats,
        # then repopulate the Treeview and labels.
        for row in tree.get_children():
            tree.delete(row)

        # Pandas: load data
        full_df = po.load_sessions_dataframe()
        _state["full_df"] = full_df

        # Pandas: groupby per client
        summary_df = po.build_summary(full_df)

        # NumPy: round currency columns
        summary_df = no.apply_rounding_to_summary(summary_df)
        _state["summary_df"] = summary_df

        # NumPy: compute overall stats
        stats = no.compute_summary_stats(full_df)
        total_hours_lbl.config(text=f"Total Hours: {stats['total_hours']}")
        avg_earn_lbl.config(
            text=f"Avg Session Earnings: ${stats['avg_session_earnings']:.2f}"
        )
        grand_total_lbl.config(
            text=f"Grand Total Earned: ${stats['grand_total_earned']:.2f}"
        )

        for _, row in summary_df.iterrows():
            tree.insert(
                "",
                "end",
                values=(
                    row["client_name"],
                    int(row["sessions"]),
                    f"{row['total_hours']:.2f}",
                    f"${row['total_earned']:.2f}",
                    f"${row['avg_session_earnings']:.2f}",
                ),
            )

    def export_csv():
        # Export summary to CSV via df.to_csv().
        if _state["summary_df"] is None or _state["summary_df"].empty:
            messagebox.showwarning("No Data", "Run a summary refresh first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Summary to CSV",
        )
        if not path:
            return  # user cancelled
        po.export_summary_to_csv(_state["summary_df"], path)
        messagebox.showinfo("Exported", f"Summary saved to:\n{path}")

    def generate_invoice():
        # Generate invoice for the selected client.
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection", "Please select a client row to generate an invoice."
            )
            return
        # Read client name from the first column of the selected row
        client_name = tree.item(selected[0], "values")[0]
        inv.save_invoice(client_name)

    # ==== Buttons ====
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", padx=10, pady=8)
    ttk.Button(btn_frame, text="Refresh Summary", command=refresh_summary).pack(
        side="left", padx=4
    )
    ttk.Button(btn_frame, text="Export to CSV", command=export_csv).pack(
        side="left", padx=4
    )
    ttk.Button(
        btn_frame, text="Generate Invoice for Selected Client", command=generate_invoice
    ).pack(side="right", padx=4)

    # Initial load
    refresh_summary()

    return refresh_summary
