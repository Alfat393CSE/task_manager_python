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
def refresh_tasks(filter_status="All", search_text=""):
    for row in tree.get_children():
        tree.delete(row)

    query = "SELECT * FROM tasks"
    params = []
    if filter_status != "All":
        query += " WHERE status=?"
        params.append(filter_status)

    if search_text:
        query += " AND title LIKE ?" if filter_status != "All" else " WHERE title LIKE ?"
        params.append(f"%{search_text}%")

    query += " ORDER BY due_date ASC"
    c.execute(query, params)

    for task in c.fetchall():
        due_date = task[3]
        try:
            if task[5] == "Pending" and due_date and datetime.strptime(due_date, "%Y-%m-%d") < datetime.today():
                tree.insert("", "end", values=task, tags=("overdue",))
            else:
                tree.insert("", "end", values=task)
        except:
            tree.insert("", "end", values=task)

    tree.tag_configure("overdue", background="tomato")

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

def search_tasks():
    search_text = search_entry.get()
    filter_status = status_var.get()
    refresh_tasks(filter_status, search_text)

def on_double_click(event):
    selected = tree.selection()
    if not selected:
        return
    task = tree.item(selected)["values"]

    editor = tk.Toplevel(root)
    editor.title("Edit Task")

    tk.Label(editor, text="Title").grid(row=0, column=0)
    title_edit = tk.Entry(editor)
    title_edit.grid(row=0, column=1)
    title_edit.insert(0, task[1])

    tk.Label(editor, text="Description").grid(row=1, column=0)
    desc_edit = tk.Text(editor, width=30, height=3)
    desc_edit.grid(row=1, column=1)
    desc_edit.insert("1.0", task[2])

    tk.Label(editor, text="Due Date (YYYY-MM-DD)").grid(row=2, column=0)
    due_edit = tk.Entry(editor)
    due_edit.grid(row=2, column=1)
    due_edit.insert(0, task[3])

    tk.Label(editor, text="Priority").grid(row=3, column=0)
    priority_edit = ttk.Combobox(editor, values=["Low", "Medium", "High"])
    priority_edit.set(task[4])
    priority_edit.grid(row=3, column=1)

    def save_changes():
        new_title = title_edit.get()
        new_desc = desc_edit.get("1.0", tk.END).strip()
        new_due = due_edit.get()
        new_priority = priority_edit.get()

        c.execute("UPDATE tasks SET title=?, description=?, due_date=?, priority=? WHERE id=?",
                  (new_title, new_desc, new_due, new_priority, task[0]))
        conn.commit()
        refresh_tasks()
        editor.destroy()

    tk.Button(editor, text="Save", command=save_changes).grid(row=4, column=0, columnspan=2)

# GUI
root = tk.Tk()
root.title("Task Manager")
root.geometry("800x600")

frame = tk.Frame(root)
frame.pack(pady=10)

# Input fields
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

# Search & Filter
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)

status_var = tk.StringVar(value="All")
ttk.Combobox(search_frame, textvariable=status_var, values=["All", "Pending", "Completed"], width=10).pack(side=tk.LEFT, padx=5)

tk.Button(search_frame, text="Search", command=search_tasks).pack(side=tk.LEFT)

# Task list
columns = ("ID", "Title", "Description", "Due Date", "Priority", "Status")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(pady=10, fill="both", expand=True)

tree.bind("<Double-1>", on_double_click)

refresh_tasks()

root.mainloop()
