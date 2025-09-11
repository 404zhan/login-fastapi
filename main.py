# main.py
import tkinter as tk
from tkinter import messagebox
import requests


API_URL = "http://127.0.0.1:8000"  # Your FastAPI backend


# ------------------ Login Function ------------------
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    try:
        # Use OAuth2PasswordRequestForm compatible data
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/login", data=data)

        if response.status_code == 200:
            token = response.json()["access_token"]
            messagebox.showinfo("Login Successful", f"Welcome {username}!")
            root.destroy()  # close login window
            import dummyapp
            dummyapp.run_app(token)


        else:
            messagebox.showerror("Login Failed", response.json()["detail"])
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")


# ------------------ Registration Window ------------------
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
            # Default role is "user" for new registrations
            response = requests.post(f"{API_URL}/register", params={"username": uname, "password": pwd})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Registration successful! Please login.")
                reg_win.destroy()
            else:
                messagebox.showerror("Error", response.json()["detail"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {e}")

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
tk.Button(root, text="Register", command=open_register).grid(row=3, column=0, columnspan=2)

root.mainloop()
