# ATC DB

import sqlite3
import re

DB_PATH="atc_users.db"


# --- Database setup ---
conn = sqlite3.connect("db/atc_users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()


# --- Create user (run once per user) ---
# -------------------------
# Validate username & password
# -------------------------
def validate_username(username):
    """
    Username format: GAU15@BOM_15 (all uppercase)
    """
    pattern = r"^[A-Z]{5}@[A-Z]{3}_[0-9]{4}$"

    if not re.match(pattern, username):
        return False, "Username must follow format: RICHA@BOM_2025"

    return True, "Valid"

def validate_password(password):
    """
    Password format: lowercase + @ + _ + ## + min 8 chars
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if password != password.lower():
        return False, "Password must be lowercase"

    if "@" not in password or "_" not in password:
        return False, "Password must contain @ and _"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, "Valid"


# -------------------------
# Create new user
# -------------------------
def create_user(username, password):
    username = username.upper()

    # Extract airport code from username
    airport_code = username.split("@")[1].split("_")[0]

    # Validate username
    valid_user, msg_user = validate_username(username)
    if not valid_user:
        return False, f"❌ {msg_user}"

    # Validate password
    valid_pass, msg_pass = validate_password(password)
    if not valid_pass:
        return False, f"❌ {msg_pass}"

    try:
        cursor.execute(
            "INSERT INTO users (username, airport_code, password) VALUES (?, ?, ?)",
            (username, airport_code, password)
        )
        conn.commit()
        return True, "✅ User created successfully"

    except sqlite3.IntegrityError as e:
        return False, f"❌ Database Error: {e}"

# -------------------------
# Login user
# -------------------------
def login(username, password):
    username = username.upper()
    password = password.lower()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    return cursor.fetchone() is not None