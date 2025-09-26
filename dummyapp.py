import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "https://login-fastapi-qalf.onrender.com"  # backend


def run_app(token, role):
    app = tk.Tk()
    app.title(f"Dummy App - {role.capitalize()} Access")

    tk.Label(app, text=f"Welcome! Role: {role}", font=("Arial", 14)).pack(pady=10)

    # Game 1 - all users
    tk.Button(app, text="Play Bouncing Ball (All Users)", command=bouncing_ball).pack(pady=5)

    # Game 2 - admin only
    if role == "admin":
        tk.Button(app, text="Play Snake (Admin Only)", command=lambda: snake_game(role)).pack(pady=5)
        # Admin-only role assignment
        tk.Button(app, text="Assign Role", command=lambda: assign_role_ui(token)).pack(pady=5)

    app.mainloop()


# Dummy placeholder games
def bouncing_ball():
    messagebox.showinfo("Game", "Bouncing Ball game starts here!")


def snake_game(role):
    if role != "admin":
        messagebox.showerror("Access Denied", "Only Admin can play Snake!")
        return
    messagebox.showinfo("Game", "Snake game starts here!")


# ------------------ Admin Role Assignment ------------------
def assign_role_ui(token):
    win = tk.Toplevel()
    win.title("Assign Role")

    tk.Label(win, text="Username").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(win, text="New Role").grid(row=1, column=0, padx=5, pady=5)

    entry_username = tk.Entry(win)
    entry_username.grid(row=0, column=1, padx=5, pady=5)

    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(win, textvariable=role_var, values=["Dealer", "factory", "service", "management", "R&D", "admin"])
    role_dropdown.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        uname = entry_username.get().strip()
        new_role = role_var.get().strip()
        if not uname or not new_role:
            messagebox.showwarning("Warning", "Both fields required")
            return

        try:
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.post(f"{API_URL}/assignrole", params={"username": uname, "new_role": new_role}, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            messagebox.showinfo("Success", data.get("msg", "Role updated"))
            win.destroy()
        except Exception as e:
            try:
                messagebox.showerror("Error", resp.json().get("detail", str(e)))
            except:
                messagebox.showerror("Error", str(e))

    tk.Button(win, text="Assign", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
