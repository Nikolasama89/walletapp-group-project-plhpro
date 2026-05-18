"""Διαχείριση σύνδεσης με τη βάση δεδομένων SQLite."""
import sqlite3
import os


# Διαδρομή για τη βάση
DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_FOLDER, "wallet.db")


# SQL για δημιουργία των πινάκων
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income','expense','both')),
    monthly_budget REAL CHECK (monthly_budget IS NULL OR monthly_budget >= 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_type TEXT NOT NULL CHECK (txn_type IN ('income','expense')),
    amount REAL NOT NULL CHECK (amount > 0),
    category_id INTEGER,
    txn_date TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL CHECK (task_type IN ('obligation','wish')),
    title TEXT NOT NULL,
    amount REAL CHECK (amount IS NULL OR amount >= 0),
    category_id INTEGER,
    due_date TEXT,
    priority INTEGER NOT NULL DEFAULT 2 CHECK (priority IN (1,2,3)),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','done','cancelled')),
    notify_days_before INTEGER NOT NULL DEFAULT 3 CHECK (notify_days_before >= 0),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
"""


# Προεπιλεγμένες κατηγορίες
DEFAULT_CATEGORIES = [
    ("Μισθός", "income"),
    ("Επιστροφή φόρου", "income"),
    ("Δώρα", "income"),
    ("Τρόφιμα", "expense"),
    ("Μετακινήσεις", "expense"),
    ("Ενοίκιο", "expense"),
    ("Λογαριασμοί", "expense"),
    ("Διασκέδαση", "expense"),
    ("Υγεία", "expense"),
    ("Ρούχα", "expense"),
    ("Άλλο", "both"),
]


class Database:
    """Κλάση για διαχείριση της βάσης δεδομένων."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Δημιούργησε τον φάκελο data/ αν δεν υπάρχει
        folder = os.path.dirname(db_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # Αρχικοποίησε το schema
        self.initialize_schema()

    def get_connection(self):
        """Επιστρέφει νέα σύνδεση με τη βάση."""
        conn = sqlite3.connect(self.db_path)
        # ΣΗΜΑΝΤΙΚΟ: ενεργοποίηση foreign keys (είναι off by default!)
        conn.execute("PRAGMA foreign_keys = ON")
        # Για να επιστρέφει rows με ονόματα στηλών (π.χ. row["name"])
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self):
        """Δημιουργεί τους πίνακες αν δεν υπάρχουν."""
        conn = self.get_connection()
        try:
            conn.executescript(SCHEMA_SQL)
            # Αν δεν υπάρχουν κατηγορίες, βάλε τις default
            cursor = conn.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            if count == 0:
                conn.executemany(
                    "INSERT INTO categories (name, type) VALUES (?, ?)",
                    DEFAULT_CATEGORIES
                )
            conn.commit()
        finally:
            conn.close()

