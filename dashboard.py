from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import session
import db

def show_user_dashboard(frame, back_callback=None):
    for widget in frame.winfo_children():
        widget.destroy()

    if not session.is_logged_in():
        Label(frame, text="Please login to view your dashboard.", fg="white", bg="#111111", font=("Arial", 14)).pack(pady=20)
        return

    user_id = session.current_user["id"]
    username = session.current_user["username"]
    balance, transactions = db.get_user_dashboard_data(user_id)

    frame.configure(bg="#111111")

    Label(frame, text=f"Welcome, {username}", font=("Arial", 18, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
    Label(frame, text=f"Account Balance: ${balance:.2f}", font=("Arial", 14), fg="white", bg="#111111").pack(pady=5)

    # Deposit / Withdraw Section
    amount_frame = Frame(frame, bg="#111111")
    amount_frame.pack(pady=10)

    Label(amount_frame, text="Amount:", font=("Arial", 12), fg="white", bg="#111111").grid(row=0, column=0, padx=5)
    amount_entry = Entry(amount_frame, font=("Arial", 12), bg="#222222", fg="white")
    amount_entry.grid(row=0, column=1, padx=5)

    def deposit():
        try:
            amount = float(amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
            db.add_transaction(user_id, "deposit", amount, "Manual Deposit")
            messagebox.showinfo("Success", f"${amount:.2f} deposited successfully.")
            show_user_dashboard(frame, back_callback)
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid positive number.")

    def withdraw():
        try:
            amount = float(amount_entry.get().strip())
            if amount <= 0:
                raise ValueError
            if amount > balance:
                messagebox.showerror("Insufficient", "You don't have enough balance.")
                return
            db.add_transaction(user_id, "withdraw", amount, "Manual Withdraw")
            messagebox.showinfo("Success", f"${amount:.2f} withdrawn successfully.")
            show_user_dashboard(frame, back_callback)
        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid positive number.")

    Button(amount_frame, text="Deposit", command=deposit, bg="#00cc99", fg="white", font=("Arial", 12), width=12).grid(row=1, column=0, pady=5)
    Button(amount_frame, text="Withdraw", command=withdraw, bg="#ff5050", fg="white", font=("Arial", 12), width=12).grid(row=1, column=1, pady=5)

    # Function Buttons Section
    buttons_frame = Frame(frame, bg="#111111")
    buttons_frame.pack(pady=10)

    buttons_frame_left = Frame(buttons_frame, bg="#111111")
    buttons_frame_left.grid(row=0, column=0, padx=10)
    
    buttons_frame_right = Frame(buttons_frame, bg="#111111")
    buttons_frame_right.grid(row=0, column=1, padx=10)

    # Left column buttons
    Button(buttons_frame_left, text="Apply for Loan", command=lambda: open_loan_form(), bg="#0066cc", fg="white", font=("Arial", 12), width=20).pack(pady=5)
    Button(buttons_frame_left, text="View My Loans", command=lambda: open_loan_list(), bg="#0055cc", fg="white", font=("Arial", 12), width=20).pack(pady=5)
    Button(buttons_frame_left, text="FD/RD Simulation", command=lambda: open_fd_rd_simulation(), bg="#6600cc", fg="white", font=("Arial", 12), width=20).pack(pady=5)

    # Right column buttons
    Button(buttons_frame_right, text="Initiate Escrow Transaction", command=lambda: open_escrow_form(), bg="#cc6600", fg="white", font=("Arial", 12), width=20).pack(pady=5)
    Button(buttons_frame_right, text="View Mini Statement", command=lambda: show_mini_statement(), bg="#3399ff", fg="white", font=("Arial", 12), width=20).pack(pady=5)
    Button(buttons_frame_right, text="Download Statement", command=lambda: download_statement(), bg="#3399ff", fg="white", font=("Arial", 12), width=20).pack(pady=5)
    Button(buttons_frame_right, text="View All Transactions", command=lambda: show_all_transactions(), bg="#FF9900", fg="white", font=("Arial", 12), width=20).pack(pady=5)

    # Recent Transactions Section
    Label(frame, text="Recent Transactions", font=("Arial", 14, "bold"), fg="#00FFCC", bg="#111111").pack(pady=(20, 10))
    if transactions:
        for t_type, amt, desc, time in transactions:
            label = f"{t_type.title()} ${amt:.2f} - {desc} ({time})"
            Label(frame, text=label, font=("Arial", 11), fg="white", bg="#111111").pack()
    else:
        Label(frame, text="No recent transactions found.", font=("Arial", 11), fg="gray", bg="#111111").pack()

    # Back button - now packed without side=BOTTOM so it appears at the end
    if back_callback:
        Button(frame, text="Back", command=back_callback, bg="#444444", fg="white", font=("Arial", 12)).pack(pady=20)

    # ---------- Inner Functions for additional features ----------
    def show_all_transactions():
        trans_win = Toplevel(frame)
        trans_win.title("All Transactions")
        trans_win.geometry("800x600")
        trans_win.configure(bg="#111111")
        
        # Title
        Label(trans_win, text="Complete Transaction History", font=("Arial", 16, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
        
        # Filter frame
        filter_frame = Frame(trans_win, bg="#111111")
        filter_frame.pack(pady=10, fill=X)
        
        Label(filter_frame, text="Filter by type:", font=("Arial", 12), fg="white", bg="#111111").pack(side=LEFT, padx=5)
        
        # Transaction type filter
        txn_type = StringVar()
        txn_type.set("All")  # Default option
        types = ["All", "Deposit", "Withdraw", "Transfer_in", "Transfer_out", "Escrow"]
        
        type_dropdown = ttk.Combobox(filter_frame, textvariable=txn_type, values=types, width=15)
        type_dropdown.pack(side=LEFT, padx=5)
        
        # Create a frame for the transactions list with scrollbar
        list_frame = Frame(trans_win, bg="#111111")
        list_frame.pack(fill=BOTH, expand=TRUE, padx=20, pady=10)
        
        # Create Treeview
        columns = ("Type", "Amount", "Description", "Date/Time")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            
        # Set column widths
        tree.column("Type", width=100)
        tree.column("Amount", width=100)
        tree.column("Description", width=350)
        tree.column("Date/Time", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=TRUE)
        
        def load_transactions():
            # Clear existing data
            for i in tree.get_children():
                tree.delete(i)
                
            # Get transactions based on filter
            if txn_type.get() == "All":
                transactions = db.get_all_transactions(user_id)
            else:
                transactions = db.get_transactions_by_type(user_id, txn_type.get().lower())
                
            # Insert data
            for i, (t_type, amount, desc, timestamp) in enumerate(transactions):
                tree.insert("", "end", values=(t_type.title(), f"${amount:.2f}", desc, timestamp))
        
        # Load transactions when filter changes
        type_dropdown.bind("<<ComboboxSelected>>", lambda e: load_transactions())
        
        # Export button
        export_frame = Frame(trans_win, bg="#111111")
        export_frame.pack(pady=10)
        
        def export_filtered():
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Filtered Transactions")
            if file_path:
                if txn_type.get() == "All":
                    db.export_transactions_to_csv(user_id, file_path)
                else:
                    db.export_filtered_transactions_to_csv(user_id, txn_type.get().lower(), file_path)
                messagebox.showinfo("Exported", "Transactions exported successfully.")
        
        Button(export_frame, text="Export Filtered List", command=export_filtered, bg="#00cc99", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)
        Button(export_frame, text="Close", command=trans_win.destroy, bg="#444444", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)
        
        # Load transactions initially
        load_transactions()

    def open_loan_form():
        loan_win = Toplevel(frame)
        loan_win.title("Loan Application")
        loan_win.geometry("350x300")
        loan_win.configure(bg="#111111")

        Label(loan_win, text="Apply for Loan", font=("Arial", 16, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
        Label(loan_win, text="Amount:", bg="#111111", fg="white").pack()
        loan_amount = Entry(loan_win, bg="#222222", fg="white")
        loan_amount.pack(pady=5)
        Label(loan_win, text="Purpose:", bg="#111111", fg="white").pack()
        loan_purpose = Entry(loan_win, bg="#222222", fg="white")
        loan_purpose.pack(pady=5)
        Label(loan_win, text="Duration (months):", bg="#111111", fg="white").pack()
        loan_duration = Entry(loan_win, bg="#222222", fg="white")
        loan_duration.pack(pady=5)

        def submit_loan():
            try:
                amount = float(loan_amount.get())
                purpose = loan_purpose.get().strip()
                duration = int(loan_duration.get())
                if amount <= 0 or duration <= 0 or not purpose:
                    raise ValueError
                status = db.apply_for_loan(user_id, amount, purpose, duration)
                messagebox.showinfo("Loan Status", f"Loan {status}!\nAmount: ${amount:.2f}")
                loan_win.destroy()
            except ValueError:
                messagebox.showerror("Invalid", "Please enter valid loan details.")
        Button(loan_win, text="Submit", command=submit_loan, bg="#3399ff", fg="white").pack(pady=15)

    def open_loan_list():
        loans = db.get_user_loans(user_id)
        loan_win = Toplevel()
        loan_win.title("My Loans")
        loan_win.configure(bg="#111111")
        Label(loan_win, text="Your Loan Applications", font=("Arial", 14, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
        if not loans:
            Label(loan_win, text="No loans found.", fg="white", bg="#111111", font=("Arial", 12)).pack(pady=10)
            return
        text_widget = Text(loan_win, bg="#222222", fg="white", font=("Arial", 11), wrap="word", width=60, height=15)
        text_widget.pack(padx=10, pady=10)
        scrollbar = Scrollbar(loan_win, command=text_widget.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        for loan in loans:
            amount, purpose, duration, status, timestamp = loan
            info = f"Amount: ${amount:.2f}\nPurpose: {purpose}\nDuration: {duration} months\nStatus: {status}\nApplied On: {timestamp}\n\n"
            text_widget.insert(END, info)
        text_widget.config(state="disabled")

    def open_fd_rd_simulation():
        sim_window = Toplevel(frame)
        sim_window.title("FD/RD Simulation")
        sim_window.configure(bg="#111111")
        Label(sim_window, text="Deposit Type:", bg="#111111", fg="white", font=("Arial", 12)).pack(pady=5)
        deposit_type = StringVar(value="FD")
        OptionMenu(sim_window, deposit_type, "FD", "RD").pack()
        Label(sim_window, text="Amount:", bg="#111111", fg="white", font=("Arial", 12)).pack(pady=5)
        amt_entry = Entry(sim_window, font=("Arial", 12), bg="#222222", fg="white")
        amt_entry.pack()
        Label(sim_window, text="Duration (months):", bg="#111111", fg="white", font=("Arial", 12)).pack(pady=5)
        duration_entry = Entry(sim_window, font=("Arial", 12), bg="#222222", fg="white")
        duration_entry.pack()
        def simulate_fd_rd():
            try:
                amount = float(amt_entry.get())
                months = int(duration_entry.get())
                rate = 0.06  # 6% annual interest
                if deposit_type.get() == "FD":
                    maturity = amount * (1 + rate * (months / 12))
                else:
                    maturity = amount * months + (amount * months * (months + 1) * rate) / (2 * 12)
                Label(sim_window, text=f"Estimated Maturity Amount: ${maturity:.2f}", fg="#00FF99", bg="#111111", font=("Arial", 12, "bold")).pack(pady=10)
            except ValueError:
                messagebox.showerror("Error", "Enter valid numeric values.")
        Button(sim_window, text="Simulate", command=simulate_fd_rd, bg="#00cc99", fg="white", font=("Arial", 12)).pack(pady=10)

    def open_escrow_form():
        escrow_win = Toplevel(frame)
        escrow_win.title("Initiate Escrow Transaction")
        escrow_win.geometry("350x350")
        escrow_win.configure(bg="#111111")
        Label(escrow_win, text="Escrow Transaction", font=("Arial", 16, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
        Label(escrow_win, text="Recipient Username:", bg="#111111", fg="white").pack()
        recipient_entry = Entry(escrow_win, bg="#222222", fg="white")
        recipient_entry.pack(pady=5)
        Label(escrow_win, text="Amount:", bg="#111111", fg="white").pack()
        amount_entry = Entry(escrow_win, bg="#222222", fg="white")
        amount_entry.pack(pady=5)
        Label(escrow_win, text="Purpose:", bg="#111111", fg="white").pack()
        purpose_entry = Entry(escrow_win, bg="#222222", fg="white")
        purpose_entry.pack(pady=5)
        def submit_escrow():
            recipient = recipient_entry.get().strip()
            purpose = purpose_entry.get().strip()
            try:
                amount = float(amount_entry.get().strip())
                if not recipient or not purpose or amount <= 0:
                    raise ValueError
                result = db.create_escrow_transaction(user_id, recipient, amount, purpose)
                messagebox.showinfo("Escrow Status", result)
                escrow_win.destroy()
            except ValueError:
                messagebox.showerror("Invalid", "Please enter valid escrow details.")
        Button(escrow_win, text="Submit", command=submit_escrow, bg="#00cc99", fg="white", font=("Arial", 12)).pack(pady=10)

    def download_statement():
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Statement As")
        if file_path:
            db.export_transactions_to_csv(user_id, file_path)
            messagebox.showinfo("Exported", "Statement downloaded successfully.")

    def show_mini_statement():
        mini_frame = Toplevel(frame)
        mini_frame.title("Mini Statement")
        mini_frame.configure(bg="#111111")
        mini_frame.geometry("450x500")
        Label(mini_frame, text="Last 10 Transactions", font=("Arial", 14, "bold"), fg="#00FFCC", bg="#111111").pack(pady=10)
        mini_txns = db.get_last_n_transactions(user_id, 10)
        if mini_txns:
            for t_type, amt, desc, time in mini_txns:
                txn_label = f"{t_type.title()} ${amt:.2f} - {desc} ({time})"
                Label(mini_frame, text=txn_label, font=("Arial", 11), fg="white", bg="#111111").pack(anchor="w", padx=20)
        else:
            Label(mini_frame, text="No transactions to show.", font=("Arial", 11), fg="gray", bg="#111111").pack()
        Button(mini_frame, text="Close", command=mini_frame.destroy, bg="#444444", fg="white", font=("Arial", 12)).pack(pady=15)