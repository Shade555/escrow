import sqlite3
import datetime

# Connect to SQLite DB
conn = sqlite3.connect("escrow_users.db")
cur = conn.cursor()

# Create users table with role
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    security_question TEXT,
    security_answer TEXT,
    balance REAL DEFAULT 0.0,
    role TEXT DEFAULT 'user'
)
""")

# Create admins table
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    security_question TEXT,
    security_answer TEXT
)
""")

# Create transactions table
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    description TEXT,
    timestamp TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Create login/logout log
cur.execute("""
CREATE TABLE IF NOT EXISTS log_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    timestamp TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()

# =================== USER FUNCTIONS ===================

def create_user(username, password, question, answer):
    try:
        cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, password, question, answer))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_login(username, password):
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cur.fetchone()

def get_user_by_username(username):
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    return cur.fetchone()

def reset_password(username, new_password):
    cur.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()

def reset_password_by_id(user_id, new_password):
    cur.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()

def update_role(user_id, new_role):
    cur.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()

def log_action(user_id, action):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO log_history (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, action, timestamp))
    conn.commit()

def get_user_dashboard_data(user_id):
    cur.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cur.fetchone()[0]

    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    transactions = cur.fetchall()

    return balance, transactions

def add_transaction(user_id, type, amount, description):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, type, amount, description, timestamp))
    
    if type == "deposit":
        cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    elif type == "withdraw":
        cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user_id))
    
    conn.commit()

def get_all_users():
    cur.execute("SELECT id, username, role FROM users")
    return cur.fetchall()

def delete_user(user_id):
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    cur.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM log_history WHERE user_id=?", (user_id,))
    conn.commit()

# =================== ADMIN FUNCTIONS ===================

def create_admin(username, password, question, answer):
    try:
        cur.execute("INSERT INTO admins (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, password, question, answer))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_admin_by_username(username):
    cur.execute("SELECT * FROM admins WHERE username=?", (username,))
    return cur.fetchone()

def reset_admin_password(username, new_password):
    cur.execute("UPDATE admins SET password=? WHERE username=?", (new_password, username))
    conn.commit()

def validate_admin_login(username, password):
    cur.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
    return cur.fetchone()

# Ensure default admin exists
def create_default_admin():
    if not get_admin_by_username("admin"):
        create_admin("admin", "admin123", "AdminAccess", "admin")
        print("[INFO] Default admin account created.")
    else:
        print("[INFO] Admin already exists.")

create_default_admin()
