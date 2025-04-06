import sqlite3
import datetime
import csv
import hashlib

DB_NAME = "escrow_users.db"

def connect():
    return sqlite3.connect(DB_NAME)

# ---------- Helper Function for Password Hashing ----------
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ---------- Initialize Tables ----------
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
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        security_question TEXT,
        security_answer TEXT
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS log_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Create loans table
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
    
    # Create escrow table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS escrow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            amount REAL,
            description TEXT,
            status TEXT,  -- e.g., 'held', 'released', 'cancelled', 'Pending'
            timestamp TEXT,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ---------- USER FUNCTIONS ----------
def create_user(username, password, question, answer):
    try:
        conn = connect()
        cur = conn.cursor()
        hashed_pw = hash_password(password)
        cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, hashed_pw, question, answer))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_login(username, password):
    conn = connect()
    cur = conn.cursor()
    hashed_pw = hash_password(password)
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
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
    hashed_pw = hash_password(new_password)
    cur.execute("UPDATE users SET password=? WHERE username=?", (hashed_pw, username))
    conn.commit()
    conn.close()

def reset_password_by_id(user_id, new_password):
    conn = connect()
    cur = conn.cursor()
    hashed_pw = hash_password(new_password)
    cur.execute("UPDATE users SET password=? WHERE id=?", (hashed_pw, user_id))
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

# ---------- ADMIN FUNCTIONS ----------
def create_admin(username, password, question, answer):
    try:
        conn = connect()
        cur = conn.cursor()
        hashed_pw = hash_password(password)
        cur.execute("INSERT INTO admins (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                    (username, hashed_pw, question, answer))
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
    hashed_pw = hash_password(new_password)
    cur.execute("UPDATE admins SET password=? WHERE username=?", (hashed_pw, username))
    conn.commit()
    conn.close()

def validate_admin_login(username, password):
    conn = connect()
    cur = conn.cursor()
    hashed_pw = hash_password(password)
    cur.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, hashed_pw))
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
    transactions = cur.fetchall()
    conn.close()
    return transactions

# ---------- LOAN FUNCTIONS ----------
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
    conn.close()

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
    conn.close()
    return status

def get_user_loans(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT amount, purpose, duration_months, status, timestamp FROM loans WHERE user_id=?", (user_id,))
    loans = cur.fetchall()
    conn.close()
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

# ---------- NEW TRANSACTION HISTORY FUNCTIONS ----------
def get_all_transactions(user_id):
    """Get all transactions for a specific user"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    transactions = cur.fetchall()
    conn.close()
    return transactions

def get_transactions_by_type(user_id, transaction_type):
    """Get transactions filtered by type for a specific user"""
    conn = connect()
    cur = conn.cursor()
    
    # Convert transaction type to lowercase to ensure consistency
    transaction_type = transaction_type.lower()
    
    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? AND LOWER(type)=? ORDER BY timestamp DESC", 
                (user_id, transaction_type))
    transactions = cur.fetchall()
    conn.close()
    return transactions

def export_filtered_transactions_to_csv(user_id, transaction_type, filepath):
    """Export filtered transactions to CSV file"""
    conn = connect()
    cur = conn.cursor()
    
    # Convert transaction type to lowercase to ensure consistency
    transaction_type = transaction_type.lower()
    
    cur.execute("SELECT type, amount, description, timestamp FROM transactions WHERE user_id=? AND LOWER(type)=? ORDER BY timestamp DESC", 
                (user_id, transaction_type))
    transactions = cur.fetchall()

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Type", "Amount", "Description", "Timestamp"])
        writer.writerows(transactions)
    
    conn.close()

# ---------- ESCROW FUNCTIONS ----------
def create_escrow_table():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS escrow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            amount REAL,
            description TEXT,
            status TEXT,  -- 'held', 'released', 'cancelled', 'Pending'
            timestamp TEXT,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

create_escrow_table()

def initiate_escrow(sender_id, receiver_username, amount, description):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username=?", (receiver_username,))
    receiver = cur.fetchone()
    if not receiver:
        conn.close()
        return False, "Receiver not found."
    receiver_id = receiver[0]

    cur.execute("SELECT balance FROM users WHERE id=?", (sender_id,))
    balance = cur.fetchone()[0]
    if amount > balance:
        conn.close()
        return False, "Insufficient funds."

    cur.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, sender_id))
    cur.execute("""
        INSERT INTO escrow (sender_id, receiver_id, amount, description, status, timestamp)
        VALUES (?, ?, ?, ?, 'held', datetime('now'))
    """, (sender_id, receiver_id, amount, description))
    conn.commit()
    conn.close()
    return True, "Escrow initiated."

def get_user_escrow(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, sender_id, receiver_id, amount, description, status, timestamp
        FROM escrow
        WHERE sender_id=? OR receiver_id=?
        ORDER BY id DESC
    """, (user_id, user_id))
    escrows = cur.fetchall()
    conn.close()
    return escrows

def release_escrow(escrow_id, receiver_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM escrow WHERE id=? AND receiver_id=? AND status='held'", (escrow_id, receiver_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Escrow not found or already processed."
    
    amount = row[0]
    cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, receiver_id))
    cur.execute("UPDATE escrow SET status='released' WHERE id=?", (escrow_id,))
    conn.commit()
    conn.close()
    return True, "Escrow released to your balance."

def cancel_escrow(escrow_id, sender_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM escrow WHERE id=? AND sender_id=? AND status='held'", (escrow_id, sender_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Escrow not found or already processed."
    
    amount = row[0]
    cur.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, sender_id))
    cur.execute("UPDATE escrow SET status='cancelled' WHERE id=?", (escrow_id,))
    conn.commit()
    conn.close()
    return True, "Escrow cancelled and refunded."

def create_escrow_transaction(sender_id, recipient_username, amount, purpose):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (recipient_username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return "Recipient not found."

    recipient_id = row[0]

    cur.execute("SELECT balance FROM users WHERE id = ?", (sender_id,))
    balance_row = cur.fetchone()
    if not balance_row or balance_row[0] < amount:
        conn.close()
        return "Insufficient funds."

    # Deduct from sender's balance
    cur.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender_id))
    
    # Record the transaction
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Record sender's escrow debit
    cur.execute("""
        INSERT INTO transactions (user_id, type, amount, description, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (sender_id, "escrow_out", amount, f"Escrow to {recipient_username}: {purpose}", timestamp))
    
    # Record recipient's escrow credit (pending)
    cur.execute("""
        INSERT INTO transactions (user_id, type, amount, description, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (recipient_id, "escrow_in", amount, f"Escrow from {get_user_by_id(sender_id)[1]}: {purpose}", timestamp))

    # Create the escrow record
    cur.execute("""
        INSERT INTO escrow (sender_id, receiver_id, amount, description, status, timestamp)
        VALUES (?, ?, ?, ?, 'Pending', ?)
    """, (sender_id, recipient_id, amount, purpose, timestamp))
    
    conn.commit()
    conn.close()
    return "Escrow transaction created successfully."

def get_pending_escrow_requests():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, 
               (SELECT username FROM users WHERE id = e.sender_id) AS sender_username,
               (SELECT username FROM users WHERE id = e.receiver_id) AS receiver_username,
               e.amount, e.description, e.timestamp
        FROM escrow e
        WHERE e.status IN (?, ?)
        ORDER BY e.timestamp DESC
    """, ("Pending", "held"))
    results = cur.fetchall()
    conn.close()
    return results

def update_escrow_status(escrow_id, new_status):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT sender_id, receiver_id, amount FROM escrow WHERE id = ?", (escrow_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "Escrow not found."

    sender_id, receiver_id, amount = row

    # Normalize the new_status to lowercase for comparison
    normalized_status = new_status.lower()

    if normalized_status == "approved":
        cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver_id))
        cur.execute("UPDATE escrow SET status = 'released' WHERE id = ?", (escrow_id,))
        result_msg = "Escrow approved and amount released to receiver."
    elif normalized_status == "rejected":
        cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, sender_id))
        cur.execute("UPDATE escrow SET status = 'cancelled' WHERE id = ?", (escrow_id,))
        result_msg = "Escrow rejected and amount refunded to sender."
    else:
        conn.close()
        return False, "Invalid status provided."

    conn.commit()
    conn.close()
    return True, result_msg

# ---------- Initialization ----------
init_db()
create_default_admin()