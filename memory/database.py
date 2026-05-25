import sqlite3
import os
import json
from datetime import datetime

# Define database location relative to the current file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db")

def get_connection():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn

def init_db():
    """Initialize the SQLite memory tables if they do not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # Create scan history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scan_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_url TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL,
        summary_vulns TEXT,  -- JSON string of vulnerability counts
        summary_tests TEXT   -- JSON string of test case counts
    )
    """)

    # Create test cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        category TEXT NOT NULL,      -- Positive, Negative, Edge Case
        test_name TEXT NOT NULL,
        description TEXT,
        steps TEXT,
        expected_result TEXT,
        FOREIGN KEY (scan_id) REFERENCES scan_history (id) ON DELETE CASCADE
    )
    """)

    # Create vulnerabilities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        severity TEXT NOT NULL,      -- High, Medium, Low, Informational
        description TEXT,
        url_path TEXT,
        remediation TEXT,
        FOREIGN KEY (scan_id) REFERENCES scan_history (id) ON DELETE CASCADE
    )
    """)

    # Create agent interactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (scan_id) REFERENCES scan_history (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def create_scan_history(target_url):
    """Start a new scan session entry in history. Returns the scan ID."""
    init_db()  # Ensure tables are ready
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO scan_history (target_url, timestamp, status, summary_vulns, summary_tests) VALUES (?, ?, ?, ?, ?)",
        (target_url, timestamp, "IN_PROGRESS", "{}", "{}")
    )
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def update_scan_status(scan_id, status, summary_vulns=None, summary_tests=None):
    """Update the status and summary metrics of an active scan."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if summary_vulns is not None and summary_tests is not None:
        cursor.execute(
            "UPDATE scan_history SET status = ?, summary_vulns = ?, summary_tests = ? WHERE id = ?",
            (status, json.dumps(summary_vulns), json.dumps(summary_tests), scan_id)
        )
    else:
        cursor.execute(
            "UPDATE scan_history SET status = ? WHERE id = ?",
            (status, scan_id)
        )
    conn.commit()
    conn.close()

def save_test_case(scan_id, category, test_name, description, steps, expected_result):
    """Save an AI-generated test case."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_cases (scan_id, category, test_name, description, steps, expected_result) VALUES (?, ?, ?, ?, ?, ?)",
        (scan_id, category, test_name, description, steps, expected_result)
    )
    conn.commit()
    conn.close()

def save_vulnerability(scan_id, name, severity, description, url_path, remediation):
    """Save a discovered vulnerability."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vulnerabilities (scan_id, name, severity, description, url_path, remediation) VALUES (?, ?, ?, ?, ?, ?)",
        (scan_id, name, severity, description, url_path, remediation)
    )
    conn.commit()
    conn.close()

def save_agent_interaction(scan_id, agent_name, message):
    """Log an interaction/message between agents in short-term context/audit logs."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO agent_interactions (scan_id, agent_name, message, timestamp) VALUES (?, ?, ?, ?)",
        (scan_id, agent_name, message, timestamp)
    )
    conn.commit()
    conn.close()

def get_scan_details(scan_id):
    """Retrieve full details of a specific scan run."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM scan_history WHERE id = ?", (scan_id,))
    scan = cursor.fetchone()
    if not scan:
        conn.close()
        return None
    scan_data = dict(scan)
    
    cursor.execute("SELECT * FROM test_cases WHERE scan_id = ?", (scan_id,))
    scan_data["test_cases"] = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM vulnerabilities WHERE scan_id = ?", (scan_id,))
    scan_data["vulnerabilities"] = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM agent_interactions WHERE scan_id = ? ORDER BY id ASC", (scan_id,))
    scan_data["agent_interactions"] = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return scan_data

def get_all_scans():
    """Retrieve summary of all scans for UI dashboard consumption."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_history ORDER BY id DESC")
    scans = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return scans

def clear_scan_history():
    """Delete all scan history (useful for reset buttons)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scan_history")
    cursor.execute("DELETE FROM test_cases")
    cursor.execute("DELETE FROM vulnerabilities")
    cursor.execute("DELETE FROM agent_interactions")
    conn.commit()
    conn.close()

# Initialize tables when database module is loaded
init_db()
