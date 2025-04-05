from tkinter import *
from tkinter import messagebox
import auth
import dashboard
import admin
import session

# Initialize main window
box = Tk()
box.title("The Escrow - Home")
box.geometry("600x600")
box.config(background="#111111")
box.resizable(False, False)

# Global Styles
btn_bg = "#222222"
btn_fg = "#FFFFFF"
btn_hover = "#00CCFF"
entry_bg = "#222222"
entry_fg = "#FFFFFF"
font_main = ("Segoe UI", 12)
font_heading = ("Segoe UI", 20, "bold")

# Hover effect
def on_enter(e):
    e.widget.config(bg=btn_hover)

def on_leave(e):
    e.widget.config(bg=btn_bg)

# Frame switch
def show_frame(frame):
    frame.tkraise()
    if frame == dashboard_frame:
        dashboard.show_user_dashboard(dashboard_frame, lambda: show_frame(home_frame))
    elif frame == admin_frame:
        admin.show_admin_panel(admin_frame, lambda: show_frame(home_frame))
    elif frame in [login_frame, signup_frame, reset_frame]:
        clear_entries()
    update_logged_in_label()

def clear_entries():
    for entry in [
        login_username, login_password,
        signup_username, signup_password, signup_question, signup_answer,
        reset_username, reset_answer, reset_newpass
    ]:
        entry.delete(0, END)

# Define Frames
home_frame = Frame(box, bg="#111111")
login_frame = Frame(box, bg="#111111")
signup_frame = Frame(box, bg="#111111")
dashboard_frame = Frame(box, bg="#111111")
reset_frame = Frame(box, bg="#111111")
admin_frame = Frame(box, bg="#111111")

for frame in (home_frame, login_frame, signup_frame, dashboard_frame, reset_frame, admin_frame):
    frame.place(x=0, y=0, width=600, height=600)

# Utility
def create_label(parent, text, size=14, bold=False, pady=10):
    return Label(parent, text=text, font=("Segoe UI", size, "bold" if bold else ""), fg=btn_fg, bg="#111111", pady=pady)

def create_entry(parent, show=None):
    return Entry(parent, font=font_main, fg=entry_fg, bg=entry_bg, width=30, bd=0, insertbackground="#FFFFFF", show=show, highlightthickness=1, highlightbackground="#444444")

def create_button(parent, text, command):
    btn = Button(parent, text=text, font=font_main, fg=btn_fg, bg=btn_bg, width=25, height=2, bd=0, command=command, activebackground=btn_hover)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

### HOME FRAME ###
Label(home_frame, text="Welcome to The Escrow", font=font_heading, fg="#00FFCC", bg="#111111").pack(pady=30)

logged_in_label = Label(home_frame, text="", font=("Segoe UI", 12), fg="#00CCFF", bg="#111111")
logged_in_label.pack(pady=5)

def update_logged_in_label():
    if session.is_logged_in():
        logged_in_label.config(text=f"Logged in as: {session.current_user['username']}")
    else:
        logged_in_label.config(text="")

def open_dashboard():
    if session.is_logged_in():
        show_frame(dashboard_frame)
    else:
        messagebox.showerror("Not Logged In", "Please log in first.")

def open_admin_panel():
    if session.is_admin():
        show_frame(admin_frame)
    else:
        messagebox.showerror("Unauthorized", "Admin access only.")

def handle_logout():
    if session.is_logged_in():
        auth.logout_user()
        update_logged_in_label()
        messagebox.showinfo("Logout", "You have been logged out.")
    else:
        messagebox.showinfo("Logout", "You're not logged in.")

# Home Buttons
for text, cmd in [
    ("Login", lambda: show_frame(login_frame)),
    ("Sign Up", lambda: show_frame(signup_frame)),
    ("Dashboard", open_dashboard),
    ("Admin Panel", open_admin_panel),
    ("Logout", handle_logout),
]:
    create_button(home_frame, text, cmd).pack(pady=10)

### LOGIN PAGE ###
create_label(login_frame, "Login", size=20, bold=True, pady=30).pack()

create_label(login_frame, "Username:").pack()
login_username = create_entry(login_frame)
login_username.pack(pady=5)

create_label(login_frame, "Password:").pack()
login_password = create_entry(login_frame, show="*")
login_password.pack(pady=5)

def try_login():
    if auth.login_user(login_username, login_password):
        show_frame(home_frame)

create_button(login_frame, "Login", try_login).pack(pady=15)
Button(login_frame, text="Forgot Password?", font=("Segoe UI", 10), fg="#00CCFF", bg="#111111", bd=0,
       command=lambda: show_frame(reset_frame)).pack()
create_button(login_frame, "Back", lambda: show_frame(home_frame)).pack(pady=10)

box.bind("<Return>", lambda e: try_login() if box.focus_get() in [login_username, login_password] else None)

### SIGN UP PAGE ###
create_label(signup_frame, "Sign Up", size=20, bold=True, pady=30).pack()

fields = [("Username:", "username"), ("Password:", "password"), ("Security Question:", "question"), ("Answer:", "answer")]
signup_username = signup_password = signup_question = signup_answer = None

for label, var in fields:
    create_label(signup_frame, label).pack()
    entry = create_entry(signup_frame, show="*" if "pass" in var else None)
    entry.pack(pady=5)
    if var == "username": signup_username = entry
    elif var == "password": signup_password = entry
    elif var == "question": signup_question = entry
    elif var == "answer": signup_answer = entry

create_button(signup_frame, "Sign Up", lambda: auth.signup_user(signup_username, signup_password, signup_question, signup_answer)).pack(pady=15)
create_button(signup_frame, "Back", lambda: show_frame(home_frame)).pack(pady=10)

### RESET PAGE ###
create_label(reset_frame, "Reset Password", size=20, bold=True, pady=30).pack()

reset_username = reset_answer = reset_newpass = None
reset_fields = [("Username:", "username"), ("Answer to Security Question:", "answer"), ("New Password:", "newpass")]

for label, var in reset_fields:
    create_label(reset_frame, label).pack()
    entry = create_entry(reset_frame, show="*" if "pass" in var else None)
    entry.pack(pady=5)
    if var == "username": reset_username = entry
    elif var == "answer": reset_answer = entry
    elif var == "newpass": reset_newpass = entry

create_button(reset_frame, "Reset Password", lambda: auth.reset_password(reset_username, reset_answer, reset_newpass)).pack(pady=15)
create_button(reset_frame, "Back", lambda: show_frame(home_frame)).pack(pady=10)

# Start
show_frame(home_frame)
box.mainloop()
