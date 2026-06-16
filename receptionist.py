import tkinter as tk
from tkinter import ttk, messagebox
import db
import theme
from datetime import datetime, timedelta

def is_name(s): return all(c.isalpha() or c.isspace() or c in "-'" for c in s)
def is_phone(s): return all(c.isdigit() or c.isspace() or c in "+-()" for c in s)

class ReceptionistPanel:
    def __init__(self, root, ssn, logout_callback):
        self.root = root
        self.root.title("RECEPTION_TERMINAL // USER: " + str(ssn))
        self.root.geometry("1100x750")
        self.logout_callback = logout_callback
        self.root.protocol("WM_DELETE_WINDOW", self.logout)
        self.my_ssn = ssn

        theme.CyberpunkTheme.apply_theme(root)
        self.colors = theme.CyberpunkTheme.get_colors()

        self.PACKAGES = {
            "Bronze": {"days": 30, "price": 1500},   
            "Gold":   {"days": 180, "price": 8000},  
            "Diamond":{"days": 365, "price": 14000}  
        }

        # Header
        header = tk.Frame(root, bg="black", height=70, highlightbackground=self.colors["accent"], highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="▒ RECEPTION_NODE // SYSTEM_ACTIVE", font=("Consolas", 18, "bold"), bg="black", fg=self.colors["accent"]).pack(side="left", padx=20)
        tk.Button(header, text="[ LOGOUT ]", bg="black", fg=self.colors["danger"], font=("Consolas", 10, "bold"), bd=0, command=self.logout).pack(side="right", padx=20)
        tk.Label(root, text=">> DOUBLE CLICK ON ROWS TO EDIT MEMBER DETAILS.", bg=self.colors["dark"], fg=self.colors["accent"], font=("Consolas", 9), anchor="w", padx=10).pack(fill="x")

        self.main_frame = tk.Frame(root, bg=self.colors["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.setup_reg()

    def logout(self):
        self.root.destroy(); self.logout_callback()

    # --- POPUP: ADD MEMBER ---
    def open_add_student_popup(self, refresh_callback):
        top = tk.Toplevel(self.root); top.title("NEW_MEMBER_ENTRY"); top.geometry("450x750"); top.configure(bg=self.colors["bg"]); top.grab_set()

        tk.Label(top, text="// NEW MEMBER REGISTRATION", font=("Consolas", 14, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=20)
        f = tk.Frame(top, bg=self.colors["bg"], padx=20); f.pack(fill="both", expand=True)

        entries = {}
        fields = [("SSN", "SSN"), ("NAME", "FirstName"), ("MIDDLE", "MiddleName"), ("SURNAME", "LastName"), ("PHONE", "Phone"), ("ADDRESS", "Address"), ("GENDER", "Gender"), ("BIRTH DATE", "BirthDate")]

        conn_tmp = db.get_db()
        try: mx = conn_tmp.execute("SELECT MAX(SSN) FROM Person").fetchone()[0]
        except: mx = None
        finally: conn_tmp.close()
        suggested_ssn = (mx or 0) + 1

        for i, (lbl, key) in enumerate(fields):
            tk.Label(f, text=lbl, bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=i, column=0, sticky="w", pady=5)
            if key == "Gender":
                e = ttk.Combobox(f, values=["Male", "Female"], state="readonly", width=23)
            else:
                e = ttk.Entry(f, width=25)
                if key in ("FirstName", "MiddleName"): e.configure(validate='key', validatecommand=(top.register(lambda P: is_name(P)), '%P'))
                if key == "Phone": e.configure(validate='key', validatecommand=(top.register(lambda P: is_phone(P)), '%P'))
            e.grid(row=i, column=1, sticky="ew", padx=10); entries[key] = e
            
            if key == "SSN":
                lbl_sugg = tk.Label(f, text=f"Hint: {suggested_ssn}", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 9))
                lbl_sugg.grid(row=i, column=2, padx=(6,0))
                lbl_sugg.bind("<Button-1>", lambda ev, ent=e, val=suggested_ssn: (ent.delete(0, 'end'), ent.insert(0, str(val))))
        
        current_row = len(fields)

        # Start Date
        tk.Label(f, text="START DATE", bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=current_row, column=0, sticky="w", pady=5)
        e_date = ttk.Entry(f, width=25); e_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        e_date.grid(row=current_row, column=1, sticky="ew", padx=10); entries["StartDate"] = e_date; current_row += 1

        # Trainer
        tk.Label(f, text="TRAINER", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 10, "bold")).grid(row=current_row, column=0, sticky="w", pady=10)
        cb_trainer = ttk.Combobox(f, state="readonly"); cb_trainer.grid(row=current_row, column=1, sticky="ew", padx=10)
        conn = db.get_db(); rows = conn.execute("SELECT P.FirstName, T.SSN FROM Trainer T JOIN Person P ON T.SSN=P.SSN").fetchall(); conn.close()
        t_map = {r[0]: r[1] for r in rows}; cb_trainer['values'] = list(t_map.keys())
        if cb_trainer['values']: cb_trainer.current(0)
        current_row += 1

        # Package
        tk.Label(f, text="PACKAGE", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 10, "bold")).grid(row=current_row, column=0, sticky="w", pady=10)
        cb_pkg = ttk.Combobox(f, state="readonly", width=23); cb_pkg.grid(row=current_row, column=1, sticky="ew", padx=10)
        pkg_display = [f"{name} - {info['price']} $" for name, info in self.PACKAGES.items()]; cb_pkg['values'] = pkg_display
        if pkg_display: cb_pkg.current(0)

        def save():
            try:
                conn=db.get_db()
                fn, mn, ph = entries["FirstName"].get(), entries["MiddleName"].get(), entries["Phone"].get()
                if any(c.isdigit() for c in fn): messagebox.showerror("INVALID", "First name must not contain numbers."); return
                if mn and any(c.isdigit() for c in mn): messagebox.showerror("INVALID", "Middle name must not contain numbers."); return
                if ph and not is_phone(ph): messagebox.showerror("INVALID", "Phone number contains invalid characters."); return
                if not entries["SSN"].get() or not cb_trainer.get() or not cb_pkg.get(): messagebox.showwarning("MISSING", "Fill required fields."); return
                
                try: start_dt = datetime.strptime(entries["StartDate"].get(), "%Y-%m-%d")
                except: messagebox.showerror("INVALID", "Date format must be YYYY-MM-DD"); return

                conn.execute("INSERT INTO Person VALUES (?,?,?,?,?,?,?)", 
                             (entries["SSN"].get(), entries["FirstName"].get(), entries["MiddleName"].get(), entries["LastName"].get(), entries["Gender"].get(), entries["BirthDate"].get(), entries["Address"].get()))
                if ph: conn.execute("INSERT INTO Person_Phone VALUES (?,?)", (entries["SSN"].get(), ph))
                conn.execute("INSERT INTO GymMember VALUES (?,?)", (entries["SSN"].get(), t_map[cb_trainer.get()]))
                
                pkg_key = cb_pkg.get().split(" - ")[0]
                price, days = self.PACKAGES[pkg_key]["price"], self.PACKAGES[pkg_key]["days"]
                end_str = (start_dt + timedelta(days=days)).strftime("%Y-%m-%d")

                conn.execute("INSERT INTO Membership (MemberSSN, ReceptionistSSN, Type, Price, StartDate, EndDate) VALUES (?,?,?,?,?,?)",
                             (entries["SSN"].get(), self.my_ssn, pkg_key, price, entries["StartDate"].get(), end_str))
                conn.commit(); messagebox.showinfo("SYSTEM", "SUCCESS"); refresh_callback(); top.destroy()
            except Exception as e: messagebox.showerror("ERROR", str(e))
            finally: conn.close()
        ttk.Button(top, text="[ SAVE ]", command=save).pack(pady=20, fill="x", padx=40)

    # --- POPUP: EDIT ---
    def open_edit_member_popup(self, ssn, refresh_callback):
        top = tk.Toplevel(self.root); top.title(f"EDIT_MEMBER_{ssn}"); top.geometry("450x700"); top.configure(bg=self.colors["bg"]); top.grab_set()
        conn = db.get_db()
        try:
            p = conn.execute("SELECT FirstName, MiddleName, LastName, Address, Gender, DateOfBirth FROM Person WHERE SSN=?", (ssn,)).fetchone()
            ph = conn.execute("SELECT PhoneNumber FROM Person_Phone WHERE SSN=?", (ssn,)).fetchone()
            m = conn.execute("SELECT TrainerSSN FROM GymMember WHERE SSN=?", (ssn,)).fetchone()
            mem = conn.execute("SELECT Type, StartDate FROM Membership WHERE MemberSSN=? ORDER BY ID DESC LIMIT 1", (ssn,)).fetchone()
            trainers = conn.execute("SELECT P.FirstName, T.SSN FROM Trainer T JOIN Person P ON T.SSN=P.SSN").fetchall()
        except: conn.close(); return
        finally: conn.close()

        t_map = {n: s for n, s in trainers}
        t_map_inv = {s: n for n, s in trainers}

        tk.Label(top, text=f"// EDIT: {p[0]} {p[2]}", font=("Consolas", 14, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=15)
        f = tk.Frame(top, bg=self.colors["bg"], padx=20); f.pack(fill="both", expand=True)
        entries = {}

        def mk_row(r, lbl, val, key, vals=None):
            tk.Label(f, text=lbl, bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=r, column=0, sticky="w", pady=5)
            if vals: e = ttk.Combobox(f, values=vals, state="readonly", width=23); e.set(val) if val else None
            else: 
                e = ttk.Entry(f, width=25); e.insert(0, str(val)) if val else None
                if key == "Phone": e.configure(validate='key', validatecommand=(top.register(lambda P: is_phone(P)), '%P'))
            e.grid(row=r, column=1, sticky="ew", padx=10); entries[key] = e

        mk_row(0, "NAME", p[0], "FirstName"); mk_row(1, "MIDDLE", p[1], "MiddleName"); mk_row(2, "SURNAME", p[2], "LastName")
        mk_row(3, "ADDRESS", p[3], "Address"); mk_row(4, "GENDER", p[4], "Gender", ["Male", "Female"])
        mk_row(5, "DOB", p[5], "BirthDate"); mk_row(6, "PHONE", ph[0] if ph else "", "Phone")

        tk.Label(f, text="TRAINER", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=7, column=0, sticky="w", pady=5)
        cb = ttk.Combobox(f, values=list(t_map.keys()), state="readonly"); cb.grid(row=7, column=1, sticky="ew", padx=10)
        if m and m[0] in t_map_inv: cb.set(t_map_inv[m[0]])
        entries["Trainer"] = cb

        tk.Label(f, text="START DATE", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=8, column=0, sticky="w", pady=5)
        e_start = ttk.Entry(f, width=25); e_start.insert(0, mem[1]) if mem and mem[1] else None
        e_start.grid(row=8, column=1, sticky="ew", padx=10); entries["StartDate"] = e_start

        tk.Label(f, text="PACKAGE", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=9, column=0, sticky="w", pady=5)
        cb_pkg = ttk.Combobox(f, values=list(self.PACKAGES.keys()), state="readonly"); cb_pkg.grid(row=9, column=1, sticky="ew", padx=10)
        if mem and mem[0] in self.PACKAGES: cb_pkg.set(mem[0])
        entries["Package"] = cb_pkg

        def update_db():
            conn = db.get_db()
            try:
                fn, mn, ph = entries["FirstName"].get(), entries["MiddleName"].get(), entries["Phone"].get()
                if any(c.isdigit() for c in fn): messagebox.showerror("INVALID", "First name error"); return
                if any(c.isdigit() for c in mn): messagebox.showerror("INVALID", "Middle name error"); return
                if ph and any(c.isalpha() for c in ph): messagebox.showerror("INVALID", "Phone error"); return

                conn.execute("UPDATE Person SET FirstName=?, MiddleName=?, LastName=?, Address=?, Gender=?, DateOfBirth=? WHERE SSN=?", 
                             (fn, mn, entries["LastName"].get(), entries["Address"].get(), entries["Gender"].get(), entries["BirthDate"].get(), ssn))
                conn.execute("DELETE FROM Person_Phone WHERE SSN=?", (ssn,))
                if ph: conn.execute("INSERT INTO Person_Phone VALUES (?,?)", (ssn, ph))
                if entries["Trainer"].get(): conn.execute("UPDATE GymMember SET TrainerSSN=? WHERE SSN=?", (t_map[entries["Trainer"].get()], ssn))
                
                new_pkg, s_date = entries["Package"].get(), entries["StartDate"].get()
                if new_pkg and new_pkg in self.PACKAGES and s_date:
                    try:
                        s_dt = datetime.strptime(s_date, "%Y-%m-%d")
                        p_info = self.PACKAGES[new_pkg]
                        e_str = (s_dt + timedelta(days=p_info["days"])).strftime("%Y-%m-%d")
                        conn.execute("UPDATE Membership SET Type=?, Price=?, StartDate=?, EndDate=? WHERE MemberSSN=? AND ID=(SELECT MAX(ID) FROM Membership WHERE MemberSSN=?)", 
                                     (new_pkg, p_info["price"], s_date, e_str, ssn, ssn))
                    except: messagebox.showerror("INVALID", "Date format error"); return

                conn.commit(); messagebox.showinfo("SYSTEM", "SUCCESS"); refresh_callback(); top.destroy()
            except Exception as e: messagebox.showerror("ERROR", str(e))
            finally: conn.close()
        ttk.Button(top, text="[ UPDATE ]", command=update_db).pack(pady=20, fill="x", padx=40)

    # --- SHOW DETAILS ---
    def show_person_details(self, ssn, role, refresh_callback):
        conn = db.get_db(); p = conn.execute("SELECT * FROM Person WHERE SSN=?", (ssn,)).fetchone(); ph = conn.execute("SELECT PhoneNumber FROM Person_Phone WHERE SSN=?", (ssn,)).fetchone()
        phone = ph[0] if ph else "N/A"; extra_info = []
        if role == "GymMember":
            m = conn.execute("SELECT Type, StartDate, EndDate FROM Membership WHERE MemberSSN=?", (ssn,)).fetchone()
            if m: 
                d = self.PACKAGES.get(m[0], {}).get("days", "?")
                extra_info = [("PACKAGE", f"{m[0]} ({d} Days)"), ("VALID", f"{m[1]} -> {m[2]}")]
            else: extra_info = [("STATUS", "NO PLAN")]
        conn.close()

        top = tk.Toplevel(self.root); top.title("DATA_CARD"); top.geometry("450x650"); top.configure(bg=self.colors["bg"])
        tk.Label(top, text=f"{p[1]} {p[2]} {p[3]}", font=("Consolas", 18, "bold"), bg=self.colors["bg"], fg="white").pack(pady=(20, 10))
        tk.Label(top, text=f"ID: {p[0]} // ROLE: {role.upper()}", font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["danger"]).pack(pady=(0, 20))
        tf = tk.Frame(top, bg=self.colors["dark"], padx=2, pady=2); tf.pack(fill="x", padx=20); tf.columnconfigure(1, weight=1)
        
        rows = [("PHONE", phone), ("ADDRESS", p[6]), ("GENDER", p[4]), ("DOB", p[5]), ("---", "---")] + extra_info
        cr = 0
        for l, v in rows:
            if l == "---": tk.Frame(tf, height=2, bg=self.colors["accent"]).grid(row=cr, column=0, columnspan=2, sticky="ew", pady=10); cr += 1; continue
            tk.Label(tf, text=l, font=("Consolas", 10, "bold"), bg=self.colors["dark"], fg=self.colors["accent"], anchor="w", pady=8, padx=10).grid(row=cr, column=0, sticky="ew")
            tk.Label(tf, text=str(v), font=("Consolas", 10), bg=self.colors["dark"], fg="white", anchor="e", pady=8, padx=10).grid(row=cr, column=1, sticky="ew")
            tk.Frame(tf, height=1, bg="#333").grid(row=cr+1, column=0, columnspan=2, sticky="ew"); cr += 2
        
        ttk.Button(top, text="[ EDIT ]", command=lambda: (top.destroy(), self.open_edit_member_popup(ssn, refresh_callback))).pack(pady=20, fill="x", padx=40)

    def setup_reg(self):
        p = self.main_frame; top = tk.Frame(p, bg=self.colors["bg"], pady=10); top.pack(fill="x", padx=10)
        cols = ("SSN", "NAME", "MIDDLE", "SURNAME", "GENDER", "DOB", "ADDRESS", "PHONE", "TRAINER", "PACKAGE", "START", "END")
        
        tf = tk.Frame(p, bg=self.colors["bg"]); tf.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(tf, columns=cols, show="headings"); ysb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview); xsb = ttk.Scrollbar(tf, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set); tree.grid(row=0, column=0, sticky="nsew"); ysb.grid(row=0, column=1, sticky="ns"); xsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1); tf.grid_columnconfigure(0, weight=1)
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center", width=85)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            conn=db.get_db()
            q = '''SELECT P.SSN, P.FirstName, P.MiddleName, P.LastName, P.Gender, P.DateOfBirth, P.Address, PH.PhoneNumber, T.FirstName, Mem.Type, Mem.StartDate, Mem.EndDate 
                   FROM GymMember M JOIN Person P ON M.SSN=P.SSN 
                   LEFT JOIN Person_Phone PH ON P.SSN=PH.SSN 
                   LEFT JOIN Trainer Tr ON M.TrainerSSN=Tr.SSN 
                   LEFT JOIN Person T ON Tr.SSN=T.SSN 
                   LEFT JOIN Membership Mem ON M.SSN=Mem.MemberSSN'''
            for r in conn.execute(q): tree.insert("", "end", values=[str(x) if x else "" for x in r])
            conn.close()
        
        tree.bind("<Double-1>", lambda e: self.show_person_details(tree.item(tree.selection())['values'][0], "GymMember", refresh))
        ttk.Button(top, text="[ ADD + ]", command=lambda: self.open_add_student_popup(refresh)).pack(side="left")
        
        def delete_member():
            sel = tree.selection()
            if sel and messagebox.askyesno("CONFIRM", "Delete record?"):
                ssn = tree.item(sel)['values'][0]; conn = db.get_db()
                for t in ["Membership", "GymMember", "Person_Phone", "Person"]: 
                    try: conn.execute(f"DELETE FROM {t} WHERE {'MemberSSN' if t=='Membership' else 'SSN'}=?", (ssn,))
                    except: pass
                conn.commit(); conn.close(); refresh()
        
        ttk.Button(top, text="[ DELETE - ]", style="Danger.TButton", command=delete_member).pack(side="right"); refresh()