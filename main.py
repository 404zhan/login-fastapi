import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from PIL import Image, ImageTk, ImageSequence

API_URL = "https://login-fastapi-qalf.onrender.com"


# ------------------ GIF Loader Widget ------------------
class GIFPlayer(ttk.Label):
    def __init__(self, parent, gif_path):
        super().__init__(parent)
        self.frames = []
        im = Image.open(gif_path)

        for frame in ImageSequence.Iterator(im):
            frame = frame.resize((40, 40), Image.LANCZOS)
            self.frames.append(ImageTk.PhotoImage(frame))

        self.index = 0
        self.animating = False

    def start(self):
        self.animating = True
        self.animate()

    def animate(self):
        if not self.animating:
            return
        self.configure(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(50, self.animate)

    def stop(self):
        self.animating = False
        self.grid_remove()


# ------------------ Background Login Worker ------------------
def perform_login(username, password, loader, btn_login, btn_register, root):
    try:
        data = {"username": username, "password": password}
        res = requests.post(f"{API_URL}/login", data=data, timeout=10)
        res.raise_for_status()

        token = res.json().get("access_token")
        if not token:
            raise ValueError("Invalid credentials")

        headers = {"Authorization": f"Bearer {token}"}
        me = requests.get(f"{API_URL}/me", headers=headers)
        me.raise_for_status()

        role = me.json().get("role", "dealer")

        messagebox.showinfo("Login Successful", f"Welcome {username}! Role: {role}")

        root.destroy()
        import dummyapp
        dummyapp.run_app(token, role)

    except Exception as e:
        messagebox.showerror("Login Error", str(e))
    finally:
        loader.stop()
        btn_login.config(state="normal")
        btn_register.config(state="normal")


# ------------------ Login Handler ------------------
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Enter username and password")
        return

    btn_login.config(state="disabled")
    btn_register.config(state="disabled")

    loader.grid(row=5, column=0, columnspan=2, pady=10)
    loader.start()

    threading.Thread(
        target=perform_login,
        args=(username, password, loader, btn_login, btn_register, root),
        daemon=True
    ).start()


# ------------------ REGISTER WINDOW ------------------
def open_register():
    reg = tk.Toplevel(root)
    reg.title("Register")
    reg.geometry("350x250")
    reg.configure(bg="#1e1e1e")

    frame = ttk.Frame(reg, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text="New Username").grid(row=0, column=0, pady=5)
    ttk.Label(frame, text="New Password").grid(row=1, column=0, pady=5)

    ent_u = ttk.Entry(frame, width=25)
    ent_p = ttk.Entry(frame, width=25, show="*")
    ent_u.grid(row=0, column=1, pady=5)
    ent_p.grid(row=1, column=1, pady=5)

    reg_loader = GIFPlayer(frame, "loading.gif")

    def perform_register(uname, pwd):
        try:
            data = {"username": uname, "password": pwd}
            res = requests.post(f"{API_URL}/register", data=data)
            res.raise_for_status()

            messagebox.showinfo("Success", "Account created! Login now.")
            reg.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            reg_loader.stop()
            btn_reg_submit.config(state="normal")

    def register_user():
        uname = ent_u.get()
        pwd = ent_p.get()

        if not uname or not pwd:
            messagebox.showerror("Error", "Fill all fields.")
            return

        btn_reg_submit.config(state="disabled")
        reg_loader.grid(row=3, column=0, columnspan=2, pady=10)
        reg_loader.start()

        threading.Thread(
            target=perform_register,
            args=(uname, pwd),
            daemon=True
        ).start()

    btn_reg_submit = ttk.Button(frame, text="Register", style="Rounded.TButton", command=register_user)
    btn_reg_submit.grid(row=2, column=0, columnspan=2, pady=10)


# ------------------ MAIN UI ------------------
root = tk.Tk()
root.title("Login")
root.geometry("380x280")
root.configure(bg="#1e1e1e")  # DARK MODE BG


# ------------------ DARK MODE + ROUNDED BUTTONS STYLE ------------------
style = ttk.Style()
style.theme_use("clam")

style.configure(
    ".",
    background="#1e1e1e",
    foreground="#dddddd",
    fieldbackground="#2c2c2c"
)

style.configure(
    "Rounded.TButton",
    background="#3a7afe",
    foreground="white",
    padding=10,
    borderwidth=0,
    focusthickness=0,
    relief="flat"
)

style.map(
    "Rounded.TButton",
    background=[("active", "#2f63d4")]
)

style.configure("TEntry", padding=5)


# ------------------ Layout ------------------
frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

ttk.Label(frame, text="Username").grid(row=0, column=0, pady=5)
ttk.Label(frame, text="Password").grid(row=1, column=0, pady=5)

entry_username = ttk.Entry(frame, width=28)
entry_password = ttk.Entry(frame, show="*", width=28)
entry_username.grid(row=0, column=1, pady=5)
entry_password.grid(row=1, column=1, pady=5)

btn_login = ttk.Button(frame, text="Login", style="Rounded.TButton", command=login_user)
btn_register = ttk.Button(frame, text="New User?", style="Rounded.TButton", command=open_register)

btn_login.grid(row=2, column=0, columnspan=2, pady=15)
btn_register.grid(row=3, column=0, columnspan=2, pady=5)

loader = GIFPlayer(frame, "loading.gif")

root.mainloop()
