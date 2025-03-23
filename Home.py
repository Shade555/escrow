from tkinter import *
from tkinter import messagebox

# Initialize the main window
box = Tk()
box.title("The Escrow - Home")
box.geometry("600x600")
box.config(background="#111111")

# Global Font & Button Styles
btn_bg = "#222222"  
btn_fg = "#FFFFFF"  
btn_hover = "#333333"
entry_bg = "#333333"  
entry_fg = "#FFFFFF"

# Function to switch frames
def show_frame(frame):
    frame.tkraise()

# Create frames
home_frame = Frame(box, bg="#111111")
login_frame = Frame(box, bg="#111111")
signup_frame = Frame(box, bg="#111111")
dashboard_frame = Frame(box, bg="#111111")  # New Dashboard Frame

for frame in (home_frame, login_frame, signup_frame, dashboard_frame):
    frame.place(x=0, y=0, width=600, height=600)

### HOME PAGE ###
title_label = Label(home_frame, text="Welcome to The Escrow", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111")
title_label.pack(pady=20)

def on_enter(e):
    e.widget.config(bg=btn_hover)

def on_leave(e):
    e.widget.config(bg=btn_bg)

# Home Page Buttons
home_buttons = [
    ("Login", lambda: show_frame(login_frame)),
    ("Sign Up", lambda: show_frame(signup_frame)),
    ("Dashboard", lambda: show_frame(dashboard_frame)),  # Dashboard Button
    ("View Balance", lambda: messagebox.showinfo("Balance", "Your balance is: $XXXX")),
    ("Deposit Money", lambda: messagebox.showinfo("Deposit", "Deposit Feature Coming Soon!")),
    ("Withdraw Money", lambda: messagebox.showinfo("Withdraw", "Withdraw Feature Coming Soon!"))
]

for text, command in home_buttons:
    btn = Button(home_frame, text=text, font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2, command=command, bd=0)
    btn.pack(pady=10)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

### LOGIN PAGE ###
Label(login_frame, text="Login", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

Label(login_frame, text="Username:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
login_username = Entry(login_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
login_username.pack(pady=5)

Label(login_frame, text="Password:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
login_password = Entry(login_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25, show="*")
login_password.pack(pady=5)

Button(login_frame, text="Login", font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2, command=lambda: messagebox.showinfo("Login", "Login Successful!")).pack(pady=10)

Button(login_frame, text="Back", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

### SIGN UP PAGE ###
Label(signup_frame, text="Sign Up", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

Label(signup_frame, text="Username:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
signup_username = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25)
signup_username.pack(pady=5)

Label(signup_frame, text="Password:", font=("Arial", 14), fg=btn_fg, bg="#111111").pack()
signup_password = Entry(signup_frame, font=("Arial", 14), fg=entry_fg, bg=entry_bg, width=25, show="*")
signup_password.pack(pady=5)

Button(signup_frame, text="Sign Up", font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2, command=lambda: messagebox.showinfo("Sign Up", "Account Created!")).pack(pady=10)

Button(signup_frame, text="Back", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

### DASHBOARD PAGE ###
Label(dashboard_frame, text="Dashboard", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111").pack(pady=20)

Label(dashboard_frame, text="Account Balance: $XXXX", font=("Arial", 14), fg=btn_fg, bg="#111111").pack(pady=5)
Label(dashboard_frame, text="Recent Transactions", font=("Arial", 14, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)

transactions = ["- $50 - Coffee", "+ $500 - Salary", "- $100 - Shopping"]
for t in transactions:
    Label(dashboard_frame, text=t, font=("Arial", 12), fg=btn_fg, bg="#111111").pack()

Button(dashboard_frame, text="Back to Home", font=("Arial", 12), fg=btn_fg, bg=btn_bg, command=lambda: show_frame(home_frame)).pack(pady=10)

# Show the home frame first
show_frame(home_frame)

# Run the app
box.mainloop()
