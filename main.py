import tkinter as tk
from tkinter import messagebox
import requests
import time

API_URL = "https://login-fastapi-qalf.onrender.com"  # Your FastAPI backend

# ------------------ Login Function ------------------
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    try:
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/login", data=data, timeout=10)
        # Raise exception for bad HTTP status
        response.raise_for_status()

        try:
            resp_json = response.json()
        except ValueError:
            messagebox.showerror("Error", f"Server returned invalid response:\n{response.text}")
            return

        token = resp_json.get("access_token")
        if token:
            # Fetch role using /me
            headers = {"Authorization": f"Bearer {token}"}
            me_resp = requests.get(f"{API_URL}/me", headers=headers)
            me_resp.raise_for_status()
            user_info = me_resp.json()
            role = user_info.get("role", "dealer")

            messagebox.showinfo("Login Successful", f"Welcome {username}! Role: {role}")
            root.destroy()
            import dummyapp
            dummyapp.run_app(token, role)  # <-- pass role along

        else:
            messagebox.showerror("Login Failed", resp_json.get("detail", "Unknown error"))

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Could not connect to server. The server might be asleep, try again in a few seconds.")
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "Request timed out. Try again.")
    except requests.exceptions.HTTPError as e:
        messagebox.showerror("Error", f"HTTP error: {e}")


# ------------------ Registration Function ------------------
def open_register():
    reg_win = tk.Toplevel(root)
    reg_win.title("Register")

    tk.Label(reg_win, text="New Username").grid(row=0, column=0)
    tk.Label(reg_win, text="New Password").grid(row=1, column=0)

    entry_reg_username = tk.Entry(reg_win)
    entry_reg_password = tk.Entry(reg_win, show="*")
    entry_reg_username.grid(row=0, column=1)
    entry_reg_password.grid(row=1, column=1)

    def register_user():
        uname = entry_reg_username.get()
        pwd = entry_reg_password.get()
        try:
            data = {"username": uname, "password": pwd}
            response = requests.post(f"{API_URL}/register?username={uname}&password={pwd}")
            response.raise_for_status()

            try:
                resp_json = response.json()
            except ValueError:
                messagebox.showerror("Error", f"Server returned invalid response:\n{response.text}")
                return

            messagebox.showinfo("Success", resp_json.get("msg", "Registration successful! Please login."))
            reg_win.destroy()

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Could not connect to server. The server might be asleep, try again in a few seconds.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Error", "Request timed out. Try again.")
        except requests.exceptions.HTTPError as e:
            try:
                error_json = response.json()
                messagebox.showerror("Error", error_json.get("detail", str(e)))
            except ValueError:
                messagebox.showerror("Error", f"HTTP error: {e}")

    tk.Button(reg_win, text="Register", command=register_user).grid(row=2, column=0, columnspan=2)


# ------------------ Tkinter Login Window ------------------
root = tk.Tk()
root.title("Login")

tk.Label(root, text="Username").grid(row=0, column=0)
tk.Label(root, text="Password").grid(row=1, column=0)

entry_username = tk.Entry(root)
entry_password = tk.Entry(root, show="*")
entry_username.grid(row=0, column=1)
entry_password.grid(row=1, column=1)

tk.Button(root, text="Login", command=login_user).grid(row=2, column=0, columnspan=2)
tk.Button(root, text="New User?", command=open_register).grid(row=3, column=0, columnspan=2)

root.mainloop()
