# Main.py

# Entry point for the Freelance Time and Pay Tracker.

# Architecture
# Main.py - builds the root window and notebook, wires tabs together
# GUI.py - all tkinter tab/widget construction
# Database.py - SQLite schema + all SQL queries
# Pandas.py - pd.read_sql, groupby, calculated columns, df.to_csv
# Numpy.py - np.sum, np.mean, np.round
# Invoice.py - plaintext invoice builder + filedialog save

import tkinter as tk
from tkinter import ttk

import Database as db
import GUI as gui


def main():

    db.init_db()  # Ensure database and tables are initialized before starting the GUI.

    # Build the main application window and tabs.
    root = tk.Tk()
    root.title("Freelance Time & Pay Tracker")
    root.geometry("820x600")
    root.minsize(700, 500)

    # Create a notebook (tabbed interface) and build each tab's UI.
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)
    client_refresh_callbacks = gui.build_clients_tab(notebook)

    # Pass the client refresh callbacks to the sessions tab so it can trigger updates when sessions change.
    gui.build_sessions_tab(notebook, client_refresh_callbacks)
    gui.build_summary_tab(notebook)

    root.mainloop()  # Start the Tkinter event loop to run the application.


if __name__ == "__main__":
    main()
