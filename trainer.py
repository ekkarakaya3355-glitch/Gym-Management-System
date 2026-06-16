import tkinter as tk
from tkinter import ttk
import db
import theme

class TrainerPanel:
    def __init__(self, root, ssn, logout_callback):
        self.root = root
        self.root.title("TRAINER_TERMINAL // ID: " + str(ssn))
        self.root.geometry("800x600")
        self.logout_callback = logout_callback
        self.root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), logout_callback()))

        theme.CyberpunkTheme.apply_theme(root)
        self.colors = theme.CyberpunkTheme.get_colors()
        
        conn = db.get_db()
        p = conn.execute("SELECT FirstName, LastName FROM Person WHERE SSN=?", (ssn,)).fetchone()
        conn.close()
        t_name = f"{p[0]} {p[1]}" if p else f"ID: {ssn}"

        h = tk.Frame(root, bg="black", height=70, highlightbackground=self.colors["accent"], highlightthickness=1)
        h.pack(fill="x")
        tk.Label(h, text=f"▒ TRAINER_NODE // {t_name}", font=("Consolas", 18, "bold"), bg="black", fg=self.colors["accent"]).pack(side="left", padx=20)
        tk.Button(h, text="[ DISCONNECT ]", bg="black", fg=self.colors["danger"], font=("Consolas", 10, "bold"), bd=0, command=lambda: (root.destroy(), logout_callback())).pack(side="right", padx=20)

        main = tk.Frame(root, bg=self.colors["bg"], padx=20, pady=20)
        main.pack(fill="both", expand=True)
        tk.Label(main, text="// ASSIGNED MEMBER LIST", font=("Consolas", 12, "bold"), bg=self.colors["bg"], fg="white").pack(anchor="w", pady=(0,10))
        
        tree = ttk.Treeview(main, columns=("Member", "Contact"), show="headings")
        tree.heading("Member", text="MEMBER NAME"); tree.heading("Contact", text="CONTACT NO")
        tree.column("Member", anchor="center"); tree.column("Contact", anchor="center")
        tree.pack(fill="both", expand=True, pady=5)

        conn=db.get_db()
        rows = conn.execute("SELECT P.FirstName || ' ' || P.LastName, PH.PhoneNumber FROM GymMember M JOIN Person P ON M.SSN=P.SSN LEFT JOIN Person_Phone PH ON P.SSN=PH.SSN WHERE M.TrainerSSN=?", (ssn,)).fetchall()
        conn.close()
        
        for r in rows: tree.insert("", "end", values=[str(x) if x else "N/A" for x in r])
        tk.Label(main, text=f">> TOTAL STUDENTS: {len(rows)}", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 10)).pack(anchor="e", pady=10)