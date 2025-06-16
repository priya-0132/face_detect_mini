import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os
import sys

leave_policy = {
    "Sick Leave": 10,
    "Casual Leave": 8,
    "Earned Leave": 6
}

def get_leave_summary(username):
    conn = mysql.connector.connect(
        host="localhost", user="root", password="root", database="facerecognitiondb"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT leave_type, COUNT(*) AS taken
        FROM leave_requests
        WHERE username = %s AND status = 'Approved'
        GROUP BY leave_type
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    summary = {lt: {"total": leave_policy[lt], "taken": 0, "remaining": leave_policy[lt]} for lt in leave_policy}
    for row in rows:
        lt = row["leave_type"]
        if lt in summary:
            summary[lt]["taken"] = row["taken"]
            summary[lt]["remaining"] = summary[lt]["total"] - row["taken"]
    return summary

def get_leave_history(username):
    conn = mysql.connector.connect(
        host="localhost", user="root", password="root", database="facerecognitiondb"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, leave_type, start_date, end_date, status, reason, document_path
        FROM leave_requests
        WHERE username = %s
        ORDER BY start_date DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def open_pdf(path):
    if os.path.exists(path):
        try:
            os.startfile(path)  # Windows only
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {e}")
    else:
        messagebox.showwarning("File Not Found", f"The document path is invalid:\n{path}")

def show_leave_details(username):
    window = tk.Toplevel()
    window.title("Leave Details")
    window.geometry("900x600")

    # Leave Summary
    tk.Label(window, text="Leave Summary", font=("Arial", 14, "bold")).pack(pady=10)
    summary = get_leave_summary(username)
    tree_summary = ttk.Treeview(window, columns=("type", "total", "taken", "remaining"), show="headings")
    for col in ("type", "total", "taken", "remaining"):
        tree_summary.heading(col, text=col.capitalize())
        tree_summary.column(col, anchor="center", width=150)
    for leave_type, data in summary.items():
        tree_summary.insert("", "end", values=(leave_type, data["total"], data["taken"], data["remaining"]))
    tree_summary.pack(pady=5)

    # Leave History
    tk.Label(window, text="Leave History", font=("Arial", 14, "bold")).pack(pady=10)
    columns = ("id", "leave_type", "start_date", "end_date", "status", "reason", "document")
    tree_history = ttk.Treeview(window, columns=columns, show="headings", height=10)
    for col in columns:
        tree_history.heading(col, text=col.replace("_", " ").title())
        tree_history.column(col, anchor="center", width=100 if col != "reason" else 200)

    rows = get_leave_history(username)
    for row in rows:
        doc = "Yes" if row["document_path"] else "No"
        tree_history.insert("", "end", values=(
            row["id"], row["leave_type"], row["start_date"], row["end_date"],
            row["status"], row["reason"], doc
        ))

    tree_history.pack(pady=10)

    def on_row_double_click(event):
        selected = tree_history.focus()
        values = tree_history.item(selected, "values")
        if not values:
            return
        doc_available = values[6] == "Yes"
        if doc_available:
            leave_id = values[0]
            conn = mysql.connector.connect(
                host="localhost", user="root", password="root", database="facerecognitiondb"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT document_path FROM leave_requests WHERE id = %s", (leave_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                open_pdf(result[0])

    tree_history.bind("<Double-1>", on_row_double_click)
    tk.Label(window, text="📁 Double-click a row with a document to open PDF", fg="gray").pack(pady=5)

def main_dashboard(username):
    root = tk.Tk()
    root.title("Employee Dashboard")
    root.geometry("400x300")

    ttk.Label(root, text=f"Welcome {username}", font=("Arial", 16)).pack(pady=30)
    ttk.Button(root, text="📄 View Leave Details", command=lambda: show_leave_details(username)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python leave.py <username> <role>")
        sys.exit(1)

    username = sys.argv[1]
    role = sys.argv[1]

    main_dashboard(username)
