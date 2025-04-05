# dashboard.py
from tkinter import *
from tkinter import messagebox
import session
import db

def show_user_dashboard(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    if not session.is_logged_in():
        Label(frame, text="Please login to view your dashboard.", fg="white", bg="#111111", font=("Arial", 14)).pack(pady=20)
        return

    balance, transactions = db.get_user_dashboard_data(session.current_user["id"])

    Label(frame, text=f"Welcome, {session.current_user['username']}", font=("Arial", 18, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
    Label(frame, text=f"Account Balance: ${balance:.2f}", font=("Arial", 14), fg="white", bg="#111111").pack(pady=5)

    def deposit():
        amount = amount_entry.get()
        if amount and amount.isdigit():
            db.add_transaction(session.current_user["id"], "deposit", float(amount), "Manual Deposit")
            messagebox.showinfo("Deposited", f"${amount} deposited successfully.")
            show_user_dashboard(frame)
        else:
            messagebox.showerror("Invalid", "Enter a valid amount.")

    def withdraw():
        amount = amount_entry.get()
        if amount and amount.isdigit():
            if float(amount) > balance:
                messagebox.showerror("Insufficient", "You don't have enough balance.")
            else:
                db.add_transaction(session.current_user["id"], "withdraw", float(amount), "Manual Withdraw")
                messagebox.showinfo("Withdrawn", f"${amount} withdrawn successfully.")
                show_user_dashboard(frame)
        else:
            messagebox.showerror("Invalid", "Enter a valid amount.")

    amount_entry = Entry(frame, font=("Arial", 12), bg="#222222", fg="white")
    amount_entry.pack(pady=5)

    Button(frame, text="Deposit", command=deposit, bg="#00cc99", fg="white", font=("Arial", 12), width=15).pack(pady=5)
    Button(frame, text="Withdraw", command=withdraw, bg="#ff5050", fg="white", font=("Arial", 12), width=15).pack(pady=5)

    Label(frame, text="Recent Transactions:", font=("Arial", 14, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
    for t in transactions:
        t_type, amt, desc, time = t
        label = f"{t_type.title()} ${amt:.2f} - {desc} ({time})"
        Label(frame, text=label, font=("Arial", 11), fg="white", bg="#111111").pack()
