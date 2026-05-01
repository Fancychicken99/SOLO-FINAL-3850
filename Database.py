"""
Database.py
-----------
Handles all SQLite database operations for the Freelance Time and Pay Tracker.
Covers: schema initialization, client CRUD, session CRUD.
Earnings are NEVER stored in the database.
They are always calculated at read time: hours x hourly_rate.
"""

import sqlite3

DB_PATH = "freelance.db"

# =======
# Schema
# =======


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    # Create the clients and sessions tables if they don't exist.

    conn = get_connection()
    cursor = conn.cursor()

    # Create clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            hourly_rate REAL NOT NULL,
            contact TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Foreign key declared inside CREATE TABLE statement

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            description TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
""")

    conn.commit()
    conn.close()


# ============
# Client CRUD
# ============

def add_client(name, hourly_rate, contact=None):
    # Add a new client to the database.
    conn = get_connection()
    try:  # try-finally to ensure connection is closed even if an error occurs
        conn.execute(
            "INSERT INTO clients (name, hourly_rate, contact) VALUES (?, ?, ?)",
            (name, hourly_rate, contact),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_clients():
    # returns a list of all clients in the database.
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, name, hourly_rate, contact, active FROM clients"
        )
        rows = cursor.fetchall()
        # Convert rows to list of dicts for easier use in the app.
        return [
            {
                "id": r[0],
                "name": r[1],
                "hourly_rate": r[2],
                "contact": r[3],
                "active": bool(r[4]),
            }
            for r in rows
        ]
    finally:
        conn.close()

def get_active_clients():
    # Returns only active clients for the session form dropdown.
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, name, hourly_rate FROM clients WHERE active = 1 ORDER BY name"
        )
        rows = cursor.fetchall()
        return [
            {"id": r[0], "name": r[1], "hourly_rate": r[2]}
            for r in rows
        ]
    finally:
        conn.close()


def archive_client(client_id):
    # Mark a client as inactive (archived).
    conn = get_connection()
    try:
        conn.execute("UPDATE clients SET active = 0 WHERE id = ?", (client_id,))
        conn.commit()
    finally:
        conn.close()


# =============
# Session CRUD
# =============


def add_session(client_id, date, hours, description=None):
    # Add a new work session to the database.
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO sessions (client_id, date, hours, description) VALUES (?, ?, ?, ?)",
            (client_id, date, hours, description),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_sessions(client_id=None):
    # Retrieve all sessions, optionally filtered by client_id.
    conn = get_connection()
    base_query = """
        SELECT
            s.id,
            s.date,
            c.name        AS client_name,
            s.hours,
            s.hours * c.hourly_rate AS earnings,
            s.description,
            s.client_id,
            c.hourly_rate
        FROM sessions s
        JOIN clients c ON s.client_id = c.id
    """
    if client_id is not None:
        cursor = conn.execute(
            base_query + " WHERE s.client_id = ? ORDER BY s.date DESC", (client_id,)
        )
    else:
        cursor = conn.execute(base_query + " ORDER BY s.date DESC")

    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "date": r[1],
            "client_name": r[2],
            "hours": r[3],
            "earnings": r[4],
            "description": r[5],
            "client_id": r[6],
            "hourly_rate": r[7],
        }
        for r in rows
    ]


def delete_session(session_id):
    # Delete a session from the database.
    conn = get_connection()
    try:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()
