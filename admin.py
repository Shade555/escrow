from tkinter import *
from tkinter import messagebox
from functools import partial  # ✅ Import partial
import db
import session

def show_admin_panel(frame, back_callback):
    for widget in frame.winfo_children():
        widget.destroy()

    if not session.is_admin():
        Label(frame, text="Access Denied: Admins only", fg="red", bg="#111111", font=("Arial", 14)).pack(pady=20)
        return

    Label(frame, text="Admin Panel - User Management", font=("Arial", 18, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)

    users = db.get_all_users()

    for user in users:
        user_id, username, role = user
        frame_row = Frame(frame, bg="#222222", pady=3)
        frame_row.pack(padx=10, pady=2, fill="x")

        Label(frame_row, text=f"{username} ({role})", font=("Arial", 12), fg="white", bg="#222222").pack(side=LEFT, padx=10)

        # ✅ All buttons now safely use partial to bind correct user_id and username
        Button(frame_row, text="Delete", command=partial(confirm_delete, user_id, username, frame, back_callback), bg="#ff4d4d", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Promote", command=partial(update_role, user_id, "admin", frame, back_callback), bg="#00cc66", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Demote", command=partial(update_role, user_id, "user", frame, back_callback), bg="#ffaa00", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Reset PW", command=partial(open_reset_popup, user_id, username, frame), bg="#3399ff", fg="white").pack(side=RIGHT, padx=5)

    Button(frame, text="Back", command=back_callback, bg="#444444", fg="white", font=("Arial", 12)).pack(pady=20)

def confirm_delete(uid, uname, frame, back_callback):
    if messagebox.askyesno("Confirm", f"Delete user '{uname}'?"):
        db.delete_user(uid)
        messagebox.showinfo("Deleted", f"User '{uname}' deleted.")
        show_admin_panel(frame, back_callback)

def update_role(uid, new_role, frame, back_callback):
    db.update_role(uid, new_role)

    # If it's the current user, refresh the session from DB
    if session.current_user["id"] == uid:
        updated_user = db.get_user_by_id(uid)
        session.login(updated_user[0], updated_user[1], updated_user[2])  # id, username, role

    show_admin_panel(frame, back_callback)


def open_reset_popup(uid, uname, frame):
    popup = Toplevel(frame)
    popup.title(f"Reset Password: {uname}")
    popup.geometry("300x150")

    Label(popup, text="New Password:").pack(pady=5)
    new_password_entry = Entry(popup, show="*")
    new_password_entry.pack(pady=5)

    def submit():
        new_pass = new_password_entry.get().strip()
        if new_pass:
            db.reset_password_by_id(uid, new_pass)
            messagebox.showinfo("Updated", f"{uname}'s password reset.")
            popup.destroy()

    Button(popup, text="Submit", command=submit).pack(pady=10)
