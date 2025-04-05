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

# Global Styles
btn_bg = "#222222"
btn_fg = "#FFFFFF"
btn_hover = "#333333"
entry_bg = "#333333"
entry_fg = "#FFFFFF"

# Frame switch function
def show_frame(frame):
    frame.tkraise()
    if frame == dashboard_frame:
        dashboard.show_user_dashboard(dashboard_frame)
    elif frame == admin_frame:
        admin.show_admin_panel(admin_frame)
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

# Hover animations
def on_enter(e):
    e.widget.config(bg=btn_hover)

def on_leave(e):
    e.widget.config(bg=btn_bg)

### HOME PAGE ###
Label(home_frame, text="Welcome to The Escrow", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

logged_in_label = Label(home_frame, text="", font=("Arial", 12), fg="#00CCFF", bg="#111111")
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
home_buttons = [
    ("Login", lambda: show_frame(login_frame)),
    ("Sign Up", lambda: show_frame(signup_frame)),
    ("Dashboard", open_dashboard),
    ("Admin Panel", open_admin_panel),
    ("Logout", handle_logout),
]

for text, cmd in home_buttons:
    btn = Button(home_frame, text=text, font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2, command=cmd, bd=0)
    btn.pack(pady=10)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

### LOGIN PAGE ###
Label(login_frame, text="Login", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

login_username = Entry(login_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
login_password = Entry(login_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25, show="*")

Label(login_frame, text="Username:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
login_username.pack(pady=5)

Label(login_frame, text="Password:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
login_password.pack(pady=5)

def try_login():
    if auth.login_user(login_username, login_password):
        show_frame(home_frame)

Button(login_frame, text="Login", font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2,
       command=try_login).pack(pady=10)

Button(login_frame, text="Forgot Password?", font=("Arial", 10), fg="#00CCFF", bg="#111111", bd=0,
       command=lambda: show_frame(reset_frame)).pack()

Button(login_frame, text="Back", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

# Enable Enter key for login
box.bind("<Return>", lambda e: try_login() if box.focus_get() in [login_username, login_password] else None)

### SIGN UP PAGE ###
Label(signup_frame, text="Sign Up", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

signup_username = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
signup_password = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25, show="*")
signup_question = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
signup_answer = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)

for text, entry in [("Username:", signup_username), ("Password:", signup_password),
                    ("Security Question:", signup_question), ("Answer:", signup_answer)]:
    Label(signup_frame, text=text, font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
    entry.pack(pady=5)

Button(signup_frame, text="Sign Up", font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2,
       command=lambda: auth.signup_user(signup_username, signup_password, signup_question, signup_answer)).pack(pady=10)

Button(signup_frame, text="Back", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

### PASSWORD RESET PAGE ###
Label(reset_frame, text="Reset Password", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

reset_username = Entry(reset_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
reset_answer = Entry(reset_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
reset_newpass = Entry(reset_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25, show="*")

for text, entry in [("Username:", reset_username), ("Answer to Security Question:", reset_answer), ("New Password:", reset_newpass)]:
    Label(reset_frame, text=text, font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
    entry.pack(pady=5)

Button(reset_frame, text="Reset Password", font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2,
       command=lambda: auth.reset_password(reset_username, reset_answer, reset_newpass)).pack(pady=10)

Button(reset_frame, text="Back", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

# Start on Home Frame
show_frame(home_frame)

# Run app
box.mainloop()
