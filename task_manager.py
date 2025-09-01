import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect("tasks.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Pending'
            )''')
conn.commit()

# Functions
def refresh_tasks():
    for row in tree.get_children():
        tree.delete(row)
    c.execute("SELECT * FROM tasks")
    for task in c.fetchall():
        tree.insert("", "end", values=task)

def add_task():
    title = title_entry.get()
    desc = desc_entry.get("1.0", tk.END).strip()
    due_date = due_entry.get()
    priority = priority_var.get()

    if not title or not due_date:
        messagebox.showwarning("Input Error", "Title and Due Date are required!")
        return

    c.execute("INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)",
              (title, desc, due_date, priority))
    conn.commit()
    refresh_tasks()

def delete_task():
    selected = tree.selection()
    if not selected:
        return
    task_id = tree.item(selected)["values"][0]
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    refresh_tasks()

def mark_completed():
    selected = tree.selection()
    if not selected:
        return
    task_id = tree.item(selected)["values"][0]
    c.execute("UPDATE tasks SET status='Completed' WHERE id=?", (task_id,))
    conn.commit()
    refresh_tasks()

# GUI
root = tk.Tk()
root.title("Task Manager")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Title:").grid(row=0, column=0)
title_entry = tk.Entry(frame)
title_entry.grid(row=0, column=1)

tk.Label(frame, text="Description:").grid(row=1, column=0)
desc_entry = tk.Text(frame, width=30, height=3)
desc_entry.grid(row=1, column=1)

tk.Label(frame, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)
due_entry = tk.Entry(frame)
due_entry.grid(row=2, column=1)

tk.Label(frame, text="Priority:").grid(row=3, column=0)
priority_var = tk.StringVar(value="Medium")
ttk.Combobox(frame, textvariable=priority_var, values=["Low", "Medium", "High"]).grid(row=3, column=1)

tk.Button(frame, text="Add Task", command=add_task).grid(row=4, column=0, pady=5)
tk.Button(frame, text="Delete Task", command=delete_task).grid(row=4, column=1, pady=5)
tk.Button(frame, text="Mark Completed", command=mark_completed).grid(row=5, column=0, columnspan=2)

# Task list
columns = ("ID", "Title", "Description", "Due Date", "Priority", "Status")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(pady=10, fill="x")

refresh_tasks()

root.mainloop()
