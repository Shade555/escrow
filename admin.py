from tkinter import *
from tkinter import messagebox
import db
import session

def show_admin_panel(frame):
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

        Button(frame_row, text="Delete", command=lambda uid=user_id, uname=username: confirm_delete(uid, uname, frame), bg="#ff4d4d", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Promote", command=lambda uid=user_id: update_role(uid, "admin", frame), bg="#00cc66", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Demote", command=lambda uid=user_id: update_role(uid, "user", frame), bg="#ffaa00", fg="white").pack(side=RIGHT, padx=5)
        Button(frame_row, text="Reset PW", command=lambda uid=user_id, uname=username: open_reset_popup(uid, uname, frame), bg="#3399ff", fg="white").pack(side=RIGHT, padx=5)

    # Back button at the bottom
    Button(frame, text="Back", command=lambda: go_back_to_dashboard(frame),
           bg="#444444", fg="white", font=("Arial", 12)).pack(pady=20)

def confirm_delete(uid, uname, frame):
    if messagebox.askyesno("Confirm", f"Delete user '{uname}'?"):
        db.delete_user(uid)
        messagebox.showinfo("Deleted", f"User '{uname}' deleted.")
        show_admin_panel(frame)

def update_role(uid, new_role, frame):
    db.update_role(uid, new_role)
    show_admin_panel(frame)

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

def go_back_to_dashboard(frame):
    from Home import show_dashboard  # Import here to avoid circular import
    show_dashboard(frame)

