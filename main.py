import tkinter as tk
from tkinter import ttk, messagebox
import db
import theme
import os
try:
    from PIL import Image, ImageTk
    _PIL = True
except:
    _PIL = False

from student import StudentPanel
from admin import AdminPanel
from receptionist import ReceptionistPanel
from trainer import TrainerPanel

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GYM_MASTER // GATEWAY")
        self.root.geometry("600x700")
        
        theme.CyberpunkTheme.apply_theme(root)
        self.colors = theme.CyberpunkTheme.get_colors()
        theme.CyberpunkTheme.center_window(root, 600, 700)

        # Grid BG
        self.canvas = tk.Canvas(root, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_grid()

        # Login Card
        self.card = tk.Frame(root, bg=self.colors["dark"], highlightbackground=self.colors["accent"], highlightthickness=2, padx=30, pady=30)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)

        # Logo handling
        img_path = os.path.join(os.path.dirname(__file__), "gym_icon.png")
        if os.path.exists(img_path):
            try:
                if _PIL:
                    img = Image.open(img_path).convert("RGBA")
                    # Resize logic
                    ratio = 80 / float(img.width)
                    new_h = int(img.height * ratio)
                    img = img.resize((80, new_h), Image.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                else:
                    self.logo_img = tk.PhotoImage(file=img_path)
                    w = self.logo_img.width()
                    factor = max(1, w // 80)
                    if factor > 1: self.logo_img = self.logo_img.subsample(factor, factor)
                
                tk.Label(self.card, image=self.logo_img, bg=self.colors["dark"]).pack(pady=(0,8))
            except: self.draw_fallback_logo()
        else: self.draw_fallback_logo()

        tk.Label(self.card, text="GYM MANAGEMENT", font=("Consolas", 20, "bold"), bg=self.colors["dark"], fg="white").pack(pady=2)
        tk.Label(self.card, text="ACCESS CONTROL TERMINAL", font=("Consolas", 9), bg=self.colors["dark"], fg=self.colors["fg"]).pack(pady=(0, 12))

        # Inputs
        tk.Label(self.card, text="ENTER IDENTITY KEY (SSN):", font=("Consolas", 10, "bold"), bg=self.colors["dark"], fg=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        self.e = ttk.Entry(self.card, font=("Consolas", 14), width=25, justify="center")
        self.e.pack(pady=(0, 25), ipady=8, fill="x")
        self.e.bind('<Return>', lambda e: self.login())

        # Buttons
        b_frame = tk.Frame(self.card, bg=self.colors["dark"])
        b_frame.pack(fill="x")
        tk.Button(b_frame, text="[ LOGIN ]", command=self.login, bg=self.colors["dark"], fg=self.colors["accent"], font=("Consolas", 11, "bold"), relief="raised").pack(fill="x", pady=5, ipady=6)
        tk.Button(b_frame, text="[ QUIT ]", command=root.destroy, bg=self.colors["dark"], fg=self.colors["danger"], font=("Consolas", 11, "bold"), relief="raised").pack(fill="x", pady=5, ipady=6)

        self.footer = tk.Label(root, text="ADMIN : 0 ", bg=self.colors["bg"], fg="#444", font=("Consolas", 8))
        self.footer.place(relx=0.5, rely=0.96, anchor="center")

    def draw_grid(self):
        w, h, step = 600, 700, 40
        for x in range(0, w, step): self.canvas.create_line(x, 0, x, h, fill="#0d1f26")
        for y in range(0, h, step): self.canvas.create_line(0, y, w, y, fill="#0d1f26")

    def draw_fallback_logo(self):
        c = tk.Canvas(self.card, width=120, height=36, bg=self.colors["dark"], highlightthickness=0)
        c.create_rectangle(14,16,106,20, fill=self.colors["fg"], outline="")
        c.create_oval(4,6,30,30, fill=self.colors["accent"], outline="")
        c.create_oval(90,6,116,30, fill=self.colors["accent"], outline="")
        c.pack(pady=(0,2))

    def login(self):
        s = self.e.get()
        if not s.isdigit(): 
            messagebox.showerror("ERROR", "Identity Key must be numeric.")
            return
        
        ssn = int(s)
        found = False

        if ssn == 0: self.open(AdminPanel); found = True
        elif self.check("Receptionist", ssn): self.open(ReceptionistPanel, ssn); found = True
        elif self.check("Trainer", ssn): self.open(TrainerPanel, ssn); found = True
        elif self.check("GymMember", ssn): self.open(StudentPanel, ssn); found = True
        
        if not found: messagebox.showerror("ACCESS DENIED", "User identity not found in database.")

    def check(self, t, s):
        conn=db.get_db()
        r=conn.execute(f"SELECT * FROM {t} WHERE SSN=?", (s,)).fetchone()
        conn.close()
        return r is not None

    def open(self, Cls, ssn=None):
        self.root.withdraw()
        top = tk.Toplevel(self.root)
        def on_out():
            self.root.deiconify(); self.e.delete(0, 'end'); self.e.focus()
        if ssn: Cls(top, ssn, on_out)
        else: Cls(top, on_out)

if __name__ == "__main__":
    db.init_db()
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()