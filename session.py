# session.py

current_user = {
    "id": None,
    "username": None,
    "role": None
}

def login(user_id, username, role):
    current_user["id"] = user_id
    current_user["username"] = username
    current_user["role"] = role
    print(f"[SESSION] Logged in as {username} (Role: {role})")  # Debug

def logout():
    print(f"[SESSION] Logged out user: {current_user['username']}")  # Debug
    current_user["id"] = None
    current_user["username"] = None
    current_user["role"] = None

def is_logged_in():
    return current_user["id"] is not None

def is_admin():
    return current_user["role"] == "admin"

def get_user_id():
    return current_user["id"]

def get_username():
    return current_user["username"]

def get_role():
    return current_user["role"]
