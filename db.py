import sqlite3
import datetime
import csv

DB_NAME = "escrow_users.db"

def connect():
    return sqlite3.connect(DB_NAME)

# Initialize tables
def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        security_question TEXT,
        security_answer TEXT,
        balance REAL DEFAULT 0.0,
        role TEXT DEFAULT 'user'
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        security_question TEXT,
        security_answer TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount REAL,
        description TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS log_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()

# =============== USER FUNCTIONS ===============

def create_user(username, password, question, answer):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, password, question, answer))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_login(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cur.fetchone()
    conn.close()
    return result

def get_user_by_id(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    result = cur.fetchone()
    conn.close()
    return result

def reset_password(username, new_password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()

def reset_password_by_id(user_id, new_password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    conn.commit()
    conn.close()

def update_role(user_id, new_role):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    cur.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM log_history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_user_dashboard_data(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    balance = cur.fetchone()[0]

    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    transactions = cur.fetchall()

    conn.close()
    return balance, transactions

def add_transaction(user_id, type, amount, description):
    conn = connect()
    cur = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, type, amount, description, timestamp))

    if type == "deposit":
        cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    elif type == "withdraw":
        cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user_id))

    conn.commit()
    conn.close()

def transfer_money(sender_id, receiver_id, amount, description):
    conn = connect()
    cur = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, sender_id))
    cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, receiver_id))

    cur.execute("INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (sender_id, "transfer_out", amount, f"To user {receiver_id}: {description}", timestamp))

    cur.execute("INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (receiver_id, "transfer_in", amount, f"From user {sender_id}: {description}", timestamp))

    conn.commit()
    conn.close()

def log_action(user_id, action):
    conn = connect()
    cur = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO log_history (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, action, timestamp))
    conn.commit()
    conn.close()

# =============== ADMIN FUNCTIONS ===============

def create_admin(username, password, question, answer):
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO admins (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, password, question, answer))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_admin_by_username(username):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admins WHERE username=?", (username,))
    admin = cur.fetchone()
    conn.close()
    return admin

def reset_admin_password(username, new_password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE admins SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()

def validate_admin_login(username, password):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
    result = cur.fetchone()
    conn.close()
    return result

def create_default_admin():
    if not get_admin_by_username("admin"):
        create_admin("admin", "admin123", "AdminAccess", "admin")
        print("[INFO] Default admin account created.")
    else:
        print("[INFO] Admin already exists.")

def get_last_n_transactions(user_id, n=10):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, n))
    return cur.fetchall()

def create_loans_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        purpose TEXT,
        duration_months INTEGER,
        status TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()

create_loans_table()

def apply_for_loan(user_id, amount, purpose, duration_months):
    conn = connect()
    cur = conn.cursor()
    status = "Approved"  # Simulated approval logic
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO loans (user_id, amount, purpose, duration_months, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, purpose, duration_months, status, timestamp))
    conn.commit()
    return status

def get_user_loans(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT amount, purpose, duration_months, status, timestamp FROM loans WHERE user_id=?", (user_id,))
    loans = cur.fetchall()
    return loans

def export_transactions_to_csv(user_id, filepath):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=?", (user_id,))
    transactions = cur.fetchall()

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Type", "Amount", "Description", "Timestamp"])
        writer.writerows(transactions)
    
    conn.close()

# Initialize DB and ensure default admin
init_db()
create_default_admin()
