from tkinter import messagebox
import db
import session

def login_user(username_entry, password_entry):
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Login Failed", "Please enter both username and password.")
        return False

    # Check regular users
    user = db.validate_login(username, password)
    if user:
        user_id, uname, *_ = user
        session.login(user_id, uname, "user")
        db.log_action(user_id, "login")
        messagebox.showinfo("Login Success", f"Welcome, {uname}!")
        return True

    # Check admins
    admin = db.validate_admin_login(username, password)
    if admin:
        admin_id, uname, *_ = admin
        session.login(admin_id, uname, "admin")
        db.log_action(admin_id, "login")
        messagebox.showinfo("Admin Login", f"Welcome Admin, {uname}!")
        return True

    messagebox.showerror("Login Failed", "Invalid username or password.")
    return False


def signup_user(username_entry, password_entry, question_entry, answer_entry):
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    question = question_entry.get().strip()
    answer = answer_entry.get().strip()

    if not (username and password and question and answer):
        messagebox.showerror("Error", "All fields are required.")
        return False

    success = db.create_user(username, password, question, answer)

    if success:
        messagebox.showinfo("Account Created", "Sign-up successful. You can now log in.")
        return True
    else:
        messagebox.showerror("Error", "Username already exists.")
        return False


def reset_password(username_entry, answer_entry, newpass_entry):
    username = username_entry.get().strip()
    answer = answer_entry.get().strip()
    newpass = newpass_entry.get().strip()

    if not username or not answer or not newpass:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Check both user and admin accounts for password reset
    user = db.get_user_by_username(username)
    if user:
        correct_answer = user[5]
        if answer.lower().strip() == correct_answer.lower().strip():
            db.reset_password(username, newpass)
            messagebox.showinfo("Success", "Password has been reset.")
        else:
            messagebox.showerror("Error", "Security answer is incorrect.")
        return

    admin = db.get_admin_by_username(username)
    if admin:
        correct_answer = admin[4]
        if answer.lower().strip() == correct_answer.lower().strip():
            db.reset_admin_password(username, newpass)
            messagebox.showinfo("Success", "Admin password has been reset.")
        else:
            messagebox.showerror("Error", "Security answer is incorrect.")
        return

    messagebox.showerror("Error", "Username not found.")


def logout_user():
    if session.is_logged_in():
        db.log_action(session.get_user_id(), "logout")
        session.logout()
