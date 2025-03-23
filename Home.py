from tkinter import *
from tkinter import messagebox

# Initialize the main window
box = Tk()
box.title("The Escrow - Home")
box.geometry("600x600")
box.config(background="#111111")

# Custom Styling
btn_bg = "#222222"  # Button background
btn_fg = "#FFFFFF"  # Button text color
btn_hover = "#333333"

# Heading Label
title_label = Label(box, text="Welcome to The Escrow", font=("Arial", 20, "bold"), fg="#00FFCC", bg="#111111")
title_label.pack(pady=20)

# Function to show message on button click
def show_message(msg):
    messagebox.showinfo("Feature", f"You clicked {msg}!")

# Button Style
def on_enter(e):
    e.widget.config(bg=btn_hover)

def on_leave(e):
    e.widget.config(bg=btn_bg)

# Buttons
buttons = [
    ("Login", lambda: show_message("Login")),
    ("Sign Up", lambda: show_message("Sign Up")),
    ("View Balance", lambda: show_message("View Balance")),
    ("Deposit Money", lambda: show_message("Deposit Money")),
    ("Withdraw Money", lambda: show_message("Withdraw Money"))
]

for text, command in buttons:
    btn = Button(box, text=text, font=("Arial", 14), fg=btn_fg, bg=btn_bg, width=20, height=2, command=command, bd=0)
    btn.pack(pady=10)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Run the app
box.mainloop()
