import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import smtplib
from email.message import EmailMessage
import pandas as pd
import calendar
import datetime
import sys

# --- Get logged-in user from command line ---
try:
    logged_user = sys.argv[1]
    logged_role = sys.argv[2].lower()
except:
    logged_user = ""
    logged_role = "user"

# --- Database Connection ---
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="attendace"
    )

# --- Email Function ---
def send_email(to, subject, content):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = "yourmail@example.com"
        msg['To'] = to

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("yourmail@example.com", "your_app_password")
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

# --- Submit Leave ---
def submit_leave():
    username = username_entry.get()
    name = name_entry.get()
    leave_type = leave_type_var.get()
    from_date = from_entry.get()
    to_date = to_entry.get()
    reason = reason_text.get("1.0", tk.END).strip()

    if not (username and name and from_date and to_date and leave_type and reason):
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    db = get_db()
    cursor = db.cursor()
    query = "INSERT INTO leave_requests (username, name, from_date, to_date, leave_type, reason) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (username, name, from_date, to_date, leave_type, reason))
    db.commit()
    db.close()
    messagebox.showinfo("Success", "Leave Request Submitted")

# --- Load Leave Requests ---
def load_requests():
    for row in tree.get_children():
        tree.delete(row)

    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, username, name, from_date, to_date, leave_type, reason, status FROM leave_requests WHERE 1"
    params = []

    if user_filter.get():
        query += " AND username=%s"
        params.append(user_filter.get())
    if from_filter.get() and to_filter.get():
        query += " AND from_date >= %s AND to_date <= %s"
        params.extend([from_filter.get(), to_filter.get()])

    cursor.execute(query, tuple(params))
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)
    db.close()

# --- Approve/Reject Request ---
def update_status(new_status):
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a leave request.")
        return

    values = tree.item(selected, 'values')
    req_id = values[0]
    username = values[1]
    name = values[2]
    from_d = values[3]
    to_d = values[4]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE leave_requests SET status=%s WHERE id=%s", (new_status, req_id))
    db.commit()

    cursor.execute("SELECT email FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    if result:
        email = result[0]
        msg = f"Dear {name}, your leave from {from_d} to {to_d} has been {new_status.lower()}."
        send_email(email, f"Leave {new_status}", msg)

    db.close()
    load_requests()

# --- Export to Excel ---
def export_excel():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM leave_requests")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if filename:
        df.to_excel(filename, index=False)
        messagebox.showinfo("Exported", "Data exported to Excel successfully.")
    db.close()

# --- Calendar View ---
def show_calendar():
    cal_win = tk.Toplevel(win)
    cal_win.title("Approved Leaves Calendar")
    cal_win.geometry("400x400")
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    cal_text = calendar.month(year, month)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT from_date, to_date, name FROM leave_requests WHERE status='Approved'")
    approved = cursor.fetchall()
    db.close()

    label = tk.Label(cal_win, text=cal_text, font=("Courier", 12), justify="left")
    label.pack()

    for (fd, td, name) in approved:
        tk.Label(cal_win, text=f"{name}: {fd} to {td}", fg="green").pack()

# --- GUI ---
win = tk.Tk()
win.title("Leave Management System")
win.geometry("1100x650")

# --- Apply Frame ---
app_frame = tk.LabelFrame(win, text="Apply for Leave", padx=10, pady=10)
app_frame.pack(fill="x", padx=10, pady=5)

tk.Label(app_frame, text="Username").grid(row=0, column=0)
username_entry = tk.Entry(app_frame)
username_entry.insert(0, logged_user)
username_entry.grid(row=0, column=1)

tk.Label(app_frame, text="Name").grid(row=0, column=2)
name_entry = tk.Entry(app_frame)
name_entry.grid(row=0, column=3)

tk.Label(app_frame, text="From (YYYY-MM-DD)").grid(row=1, column=0)
from_entry = tk.Entry(app_frame)
from_entry.grid(row=1, column=1)

tk.Label(app_frame, text="To (YYYY-MM-DD)").grid(row=1, column=2)
to_entry = tk.Entry(app_frame)
to_entry.grid(row=1, column=3)

tk.Label(app_frame, text="Leave Type").grid(row=2, column=0)
leave_type_var = tk.StringVar()
leave_type_dropdown = ttk.Combobox(app_frame, textvariable=leave_type_var, values=["Sick", "Casual", "Paid", "Emergency"])
leave_type_dropdown.grid(row=2, column=1)

tk.Label(app_frame, text="Reason").grid(row=3, column=0)
reason_text = tk.Text(app_frame, width=60, height=3)
reason_text.grid(row=3, column=1, columnspan=3)

tk.Button(app_frame, text="Apply for Leave", command=submit_leave, bg="green", fg="white").grid(row=4, column=1, pady=10)

# --- Admin Panel ---
if logged_role in ['admin', 'root']:
    admin_frame = tk.LabelFrame(win, text="Leave Requests (Admin Panel)", padx=10, pady=10)
    admin_frame.pack(fill="both", expand=True, padx=10, pady=5)

    filter_frame = tk.Frame(admin_frame)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="User:").grid(row=0, column=0)
    user_filter = tk.Entry(filter_frame, width=15)
    user_filter.grid(row=0, column=1)

    tk.Label(filter_frame, text="From Date:").grid(row=0, column=2)
    from_filter = tk.Entry(filter_frame, width=15)
    from_filter.grid(row=0, column=3)

    tk.Label(filter_frame, text="To Date:").grid(row=0, column=4)
    to_filter = tk.Entry(filter_frame, width=15)
    to_filter.grid(row=0, column=5)

    tk.Button(filter_frame, text="Filter", command=load_requests).grid(row=0, column=6, padx=10)

    cols = ("ID", "Username", "Name", "From", "To", "Type", "Reason", "Status")
    tree = ttk.Treeview(admin_frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=120)
    tree.pack(fill="both", expand=True)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Approve", command=lambda: update_status("Approved"), bg="blue", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Reject", command=lambda: update_status("Rejected"), bg="red", fg="white", width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Export to Excel", command=export_excel, bg="orange", fg="black", width=18).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="View Calendar", command=show_calendar, bg="purple", fg="white", width=18).pack(side=tk.LEFT, padx=10)

    load_requests()

win.mainloop()
