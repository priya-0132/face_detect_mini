import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import pandas as pd

# 🎨 Modern Styling
BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"
BTN_COLOR = "#3498DB"
BTN_HOVER = "#2980B9"

# 🔹 Connect to MySQL Database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="facerecognitiondb"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# 🔹 Fetch all users from the database
def fetch_users():
    conn = connect_db()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# 🔹 Insert a new user
def insert_user(username, password, email, role, major, starting_year):
    if not username or not password or not email or not role:
        messagebox.showerror("Error", "All fields except Major and Starting Year are required!")
        return
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, email, role, major, starting_year) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, password, email, role, major, starting_year)
    )
    conn.commit()
    conn.close()
    populate_treeview(user_tree)

# 🔹 Update existing user
def update_user(user_id, username, password, email, role, major, starting_year):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET username=%s, password=%s, email=%s, role=%s, major=%s, starting_year=%s WHERE id=%s",
        (username, password, email, role, major, starting_year, user_id)
    )
    conn.commit()
    conn.close()
    populate_treeview(user_tree)

# 🔹 Delete user
def delete_user(user_id):
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
        conn = connect_db()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        conn.close()
        populate_treeview(user_tree)

# 🔹 Populate Treeview
def populate_treeview(tree):
    for row in tree.get_children():
        tree.delete(row)
    users = fetch_users()
    for i, user in enumerate(users):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=user, tags=(tag,))

# 🔹 Export to Excel Function
def export_to_excel():
    try:
        # Fetching all the rows from the TreeView
        rows = user_tree.get_children()
        data = []
        
        for row in rows:
            data.append(user_tree.item(row)['values'])

        # Creating a DataFrame from the data
        df = pd.DataFrame(data, columns=["ID", "Username", "Password", "Email", "Role", "Major", "Starting Year","salary","totsl","avv","abb"])

        # File path for export
        file_path = "users_data.xlsx"
        
        # Writing to Excel file
        df.to_excel(file_path, index=False, engine="openpyxl")

        messagebox.showinfo("Export Successful", f"Data has been exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred while exporting to Excel: {e}")

# 🌟 Main GUI
root = tk.Tk()  # This is where 'root' is defined
root.title("User Management System")
root.geometry("950x500")
root.configure(bg=BG_COLOR)

# ✅ Table Frame
frame = tk.Frame(root, bg=BG_COLOR)
frame.pack(pady=10, padx=10, fill="both", expand=True)

tree_frame = tk.Frame(frame)
tree_frame.pack(fill="both", expand=True)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side="right", fill="y")

user_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,
                         columns=("ID", "Username", "Email", "Password", "Role", "Major", "Starting Year"),
                         show="headings")
tree_scroll.config(command=user_tree.yview)

for col in user_tree["columns"]:
    user_tree.heading(col, text=col)
    user_tree.column(col, anchor="center", width=120)

user_tree.tag_configure("evenrow", background="#ECF0F1")
user_tree.tag_configure("oddrow", background="#BDC3C7")
user_tree.pack(fill="both", expand=True)

# Edit/Add User
def open_edit_window(user=None):
    def save():
        user_id = user[0] if user else None
        username = entries["Username"].get()
        password = entries["Password"].get()
        email = entries["Email"].get()
        role = role_combobox.get()
        major = entries["Major"].get()
        starting_year = entries["Starting Year"].get()

        if user_id:
            update_user(user_id, username, password, email, role, major, starting_year)
        else:
            insert_user(username, password, email, role, major, starting_year)
        edit_window.destroy()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit User")
    edit_window.configure(bg=BG_COLOR)
    edit_window.geometry("300x350")

    fields = ["Username", "Password", "Email", "Role", "Major", "Starting Year"]
    entries = {}

    for idx, field in enumerate(fields):
        tk.Label(edit_window, text=field, bg=BG_COLOR, fg=FG_COLOR).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
        if field == "Role":
            role_combobox = ttk.Combobox(edit_window, values=["admin", "user"])
            role_combobox.grid(row=idx, column=1, padx=10, pady=5)
            entries["Role"] = role_combobox
        else:
            entry = tk.Entry(edit_window, bg="white", fg="black", width=25, show="*" if field == "Password" else "")
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entries[field] = entry

    if user:
        entries["Username"].insert(0, user[1])
        entries["Password"].insert(0, user[2])
        entries["Email"].insert(0, user[3])
        role_combobox.set(user[4])
        entries["Major"].insert(0, user[5] if user[5] else "")
        entries["Starting Year"].insert(0, user[6] if user[6] else "")

    tk.Button(edit_window, text="Save", command=save, bg=BTN_COLOR, fg="white").grid(row=len(fields), column=1, pady=10)

# Buttons for CRUD operations
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

add_btn = tk.Button(button_frame, text="Add User", command=lambda: open_edit_window())
add_btn.pack(side="left", padx=10)

edit_btn = tk.Button(button_frame, text="Edit User", command=lambda: open_edit_window(user_tree.item(user_tree.selection())["values"]) if user_tree.selection() else None)
edit_btn.pack(side="left", padx=10)

delete_btn = tk.Button(button_frame, text="Delete User", command=lambda: delete_user(user_tree.item(user_tree.selection())["values"][0]) if user_tree.selection() else None)
delete_btn.pack(side="left", padx=10)

# Add Export to Excel Button
export_btn = tk.Button(root, text="Export to Excel", command=export_to_excel)
export_btn.pack(pady=10)

# Load user data
populate_treeview(user_tree)

# Run GUI
root.mainloop()
