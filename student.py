import tkinter as tk
from tkinter import ttk
import db
import theme

class StudentPanel:
    def __init__(self, root, ssn, logout_callback):
        self.root = root
        self.root.title("MEMBER_ACCESS // ID: " + str(ssn))
        self.root.geometry("600x600")
        self.logout_callback = logout_callback
        self.root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), logout_callback()))

        theme.CyberpunkTheme.apply_theme(root)
        self.colors = theme.CyberpunkTheme.get_colors()

        # Header
        h = tk.Frame(root, bg="black", height=70, highlightbackground=self.colors["accent"], highlightthickness=1)
        h.pack(fill="x")
        tk.Label(h, text="▒ MEMBER_PROFILE", font=("Consolas", 18, "bold"), bg="black", fg=self.colors["accent"]).pack(side="left", padx=20)
        
        # --- FETCH DATA ---
        conn = db.get_db()
        p = conn.execute("SELECT FirstName, LastName FROM Person WHERE SSN=?", (ssn,)).fetchone()
        m = conn.execute("SELECT Type, StartDate, EndDate FROM Membership WHERE MemberSSN=?", (ssn,)).fetchone()
        t = conn.execute('SELECT P.FirstName, P.LastName FROM GymMember G JOIN Person P ON G.TrainerSSN = P.SSN WHERE G.SSN=?', (ssn,)).fetchone()
        conn.close()

        # Profile Card
        card = tk.LabelFrame(root, text="// PERSONAL DATA", padx=30, pady=30, bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 12, "bold"))
        card.pack(expand=True, padx=40, pady=40, fill="x")

        # Name
        tk.Label(card, text="FULL NAME:", bg=self.colors["bg"], fg="white", font=("Consolas", 10)).pack(anchor="w")
        tk.Label(card, text=f"{p[0]} {p[1]}", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 16, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Trainer
        tk.Label(card, text="ASSIGNED TRAINER:", bg=self.colors["bg"], fg="white", font=("Consolas", 10)).pack(anchor="w")
        t_name = f"{t[0]} {t[1]}" if t else "PENDING ASSIGNMENT"
        tk.Label(card, text=t_name, bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 14, "bold")).pack(anchor="w", pady=(0, 20))

        # Status
        tk.Label(card, text="MEMBERSHIP STATUS:", bg=self.colors["bg"], fg="white", font=("Consolas", 10)).pack(anchor="w")
        if m:
            status_text = f"ACTIVE // {m[0].upper()} CLASS\nVALID: {m[1]} -> {m[2]}"
            color = self.colors["accent"]
        else:
            status_text = "INACTIVE // NO PLAN FOUND"
            color = self.colors["danger"]

        tk.Label(card, text=status_text, bg=self.colors["bg"], fg=color, font=("Consolas", 14, "bold"), justify="left").pack(anchor="w")
        
        ttk.Button(root, text="[ LOGOUT ]", style="Danger.TButton", command=lambda: (root.destroy(), logout_callback())).pack(pady=20, padx=40, fill="x")