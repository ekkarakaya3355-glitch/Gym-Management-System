import tkinter as tk
from tkinter import ttk, messagebox
import db
import theme
from datetime import datetime, timedelta

def is_phone(s): return all(c.isdigit() or c.isspace() or c in "+-()" for c in s)
def is_salary(s):
    try: float(s); return True
    except: return s == ""

class AdminPanel:
    def __init__(self, root, logout_callback):
        self.root = root
        self.root.title("GYM SYSTEM // ADMIN_ACCESS")
        self.root.geometry("1200x750")
        self.logout_callback = logout_callback
        self.root.protocol("WM_DELETE_WINDOW", self.logout)
        
        theme.CyberpunkTheme.apply_theme(root)
        self.colors = theme.CyberpunkTheme.get_colors()

        self.PACKAGES = {"Bronze": {"days": 30, "price": 1500}, "Gold": {"days": 180, "price": 8000}, "Diamond": {"days": 365, "price": 14000}}

        # Header
        h = tk.Frame(root, bg="black", height=70, highlightbackground=self.colors["accent"], highlightthickness=1)
        h.pack(fill="x")
        tk.Label(h, text="▒ GYM_MASTER // SYSTEM_ADMIN", font=("Consolas", 18, "bold"), bg="black", fg=self.colors["accent"]).pack(side="left", padx=20)
        tk.Button(h, text="[ LOGOUT ]", bg="black", fg=self.colors["danger"], font=("Consolas", 10, "bold"), bd=0, command=self.logout).pack(side="right", padx=20)
        tk.Label(root, text=">> DOUBLE CLICK ROWS FOR DETAILS.", bg=self.colors["dark"], fg=self.colors["accent"], font=("Consolas", 9), anchor="w", padx=10).pack(fill="x", pady=(0, 10))

        # Tabs
        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabs = {}
        for n in ["PERSONNEL: RECEPTIONIST", "PERSONNEL: TRAINER", "GYM MEMBER", "EQUIPMENT INVENTORY"]:
            f = ttk.Frame(nb); nb.add(f, text=n); self.tabs[n] = f

        self.setup_hr("PERSONNEL: RECEPTIONIST", "Receptionist")
        self.setup_hr("PERSONNEL: TRAINER", "Trainer")
        self.setup_student_control()
        self.setup_equipment()

    def logout(self): self.root.destroy(); self.logout_callback()

    # --- ADD PERSONNEL ---
    def open_add_person_popup(self, role_table, refresh_callback):
        top = tk.Toplevel(self.root); top.title("ADD_PERSONNEL"); top.geometry("450x700"); top.configure(bg=self.colors["bg"]); top.grab_set()
        
        tk.Label(top, text=f"// {role_table.upper()} MODULE", font=("Consolas", 14, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=20)
        f = tk.Frame(top, bg=self.colors["bg"], padx=20); f.pack(fill="both", expand=True)

        entries = {}
        fields = [("SSN", "SSN"), ("NAME", "FirstName"), ("MIDDLE", "MiddleName"), ("SURNAME", "LastName"), ("PHONE", "Phone"), ("ADDRESS", "Address"), ("GENDER", "Gender"), ("BIRTH DATE", "DateOfBirth"), ("SALARY", "Salary")]
        
        conn = db.get_db()
        try: mx = conn.execute("SELECT MAX(SSN) FROM Person").fetchone()[0]
        except: mx = None
        sugg = (mx or 0) + 1; conn.close()
        
        extra_lbl = "SHIFT" if role_table == "Receptionist" else "BRANCH"
        fields.append((extra_lbl, "Extra"))

        for i, (lbl, key) in enumerate(fields):
            tk.Label(f, text=lbl, bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=i, column=0, sticky="w", pady=5)
            if key == "Gender": e = ttk.Combobox(f, values=["Male", "Female"], state="readonly", width=23)
            elif key == "Extra" and role_table == "Receptionist": e = ttk.Combobox(f, values=["Day", "Night"], state="readonly", width=23)
            else: e = ttk.Entry(f, width=25)
            e.grid(row=i, column=1, sticky="ew", padx=10); entries[key] = e
            
            if key == "SSN":
                l = tk.Label(f, text=f"Hint: {sugg}", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 9))
                l.grid(row=i, column=2, padx=(6,0))
                l.bind("<Button-1>", lambda ev, ent=e, val=sugg: (ent.delete(0, 'end'), ent.insert(0, str(val))))

        def save():
            try:
                fn, mn = entries["FirstName"].get(), entries["MiddleName"].get()
                if any(c.isdigit() for c in fn + mn): messagebox.showerror("INVALID", "Name contains numbers."); return
                if not entries["SSN"].get(): return
                
                conn = db.get_db()
                conn.execute("INSERT INTO Person VALUES (?,?,?,?,?,?,?)", 
                             (entries["SSN"].get(), fn, mn, entries["LastName"].get(), entries["Gender"].get(), entries["DateOfBirth"].get(), entries["Address"].get()))
                if entries["Phone"].get(): conn.execute("INSERT INTO Person_Phone VALUES (?,?)", (entries["SSN"].get(), entries["Phone"].get()))
                
                conn.execute(f"INSERT INTO {role_table} VALUES (?,?,?,?)", (entries["SSN"].get(), entries["Extra"].get(), entries["Salary"].get(), "2023-01-01"))
                conn.commit(); refresh_callback(); top.destroy(); messagebox.showinfo("SYSTEM", "SUCCESS")
            except Exception as e: messagebox.showerror("ERROR", str(e))
            finally: conn.close()
        ttk.Button(top, text="[ SAVE ]", command=save).pack(pady=20, fill="x", padx=40)

    # --- ADD MEMBER ---
    def open_add_student_popup(self, refresh_callback):
        top = tk.Toplevel(self.root); top.title("ADD_MEMBER"); top.geometry("450x700"); top.configure(bg=self.colors["bg"]); top.grab_set()
        tk.Label(top, text="// NEW MEMBER", font=("Consolas", 14, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=20)
        f = tk.Frame(top, bg=self.colors["bg"], padx=20); f.pack(fill="both", expand=True)

        entries = {}
        fields = [("SSN", "SSN"), ("NAME", "FirstName"), ("MIDDLE", "MiddleName"), ("SURNAME", "LastName"), ("PHONE", "Phone"), ("ADDRESS", "Address")]
        
        conn=db.get_db()
        try: mx = conn.execute("SELECT MAX(SSN) FROM Person").fetchone()[0]
        except: mx = None
        sugg = (mx or 0) + 1

        for i, (lbl, key) in enumerate(fields):
            tk.Label(f, text=lbl, bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=i, column=0, sticky="w", pady=5)
            e = ttk.Entry(f, width=25); e.grid(row=i, column=1, sticky="ew", padx=10); entries[key] = e
            if key == "SSN":
                l = tk.Label(f, text=f"Hint: {sugg}", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 9))
                l.grid(row=i, column=2, padx=(6,0)); l.bind("<Button-1>", lambda ev, ent=e, val=sugg: (ent.delete(0, 'end'), ent.insert(0, str(val))))

        row_idx = len(fields)
        tk.Label(f, text="START DATE", bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=row_idx, column=0, sticky="w", pady=5)
        ed = ttk.Entry(f, width=25); ed.insert(0, datetime.now().strftime("%Y-%m-%d")); ed.grid(row=row_idx, column=1, sticky="ew", padx=10); entries["StartDate"]=ed; row_idx+=1

        tk.Label(f, text="TRAINER", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=row_idx, column=0, sticky="w", pady=10)
        cb_t = ttk.Combobox(f, state="readonly"); cb_t.grid(row=row_idx, column=1, sticky="ew", padx=10)
        trs = conn.execute("SELECT P.FirstName, T.SSN FROM Trainer T JOIN Person P ON T.SSN=P.SSN").fetchall()
        t_map = {n: s for n, s in trs}; cb_t['values'] = list(t_map.keys()); cb_t.current(0) if trs else None; row_idx+=1

        tk.Label(f, text="PACKAGE", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=row_idx, column=0, sticky="w", pady=10)
        cb_p = ttk.Combobox(f, state="readonly"); cb_p.grid(row=row_idx, column=1, sticky="ew", padx=10)
        p_disp = [f"{k} - {v['price']}$" for k, v in self.PACKAGES.items()]; cb_p['values'] = p_disp; cb_p.current(0) if p_disp else None; conn.close()

        def save():
            try:
                s_dt = datetime.strptime(entries["StartDate"].get(), "%Y-%m-%d")
                conn = db.get_db()
                conn.execute("INSERT INTO Person VALUES (?,?,?,?,?,?,?)", 
                             (entries["SSN"].get(), entries["FirstName"].get(), entries["MiddleName"].get(), entries["LastName"].get(), "Male", "2000-01-01", entries["Address"].get())) # Default Gender/DOB for speed
                if entries["Phone"].get(): conn.execute("INSERT INTO Person_Phone VALUES (?,?)", (entries["SSN"].get(), entries["Phone"].get()))
                conn.execute("INSERT INTO GymMember VALUES (?,?)", (entries["SSN"].get(), t_map[cb_t.get()]))
                
                pk = cb_p.get().split(" - ")[0]
                pr, days = self.PACKAGES[pk]["price"], self.PACKAGES[pk]["days"]
                e_str = (s_dt + timedelta(days=days)).strftime("%Y-%m-%d")
                conn.execute("INSERT INTO Membership (MemberSSN, ReceptionistSSN, Type, Price, StartDate, EndDate) VALUES (?,?,?,?,?,?)",
                             (entries["SSN"].get(), 0, pk, pr, entries["StartDate"].get(), e_str))
                conn.commit(); refresh_callback(); top.destroy(); messagebox.showinfo("SYSTEM", "SUCCESS")
            except Exception as e: messagebox.showerror("ERROR", str(e))
            finally: conn.close()
        ttk.Button(top, text="[ SAVE ]", command=save).pack(pady=20, fill="x", padx=40)

    # --- EDIT POPUP ---
    def open_edit_popup(self, ssn, role, refresh_callback):
        top = tk.Toplevel(self.root); top.title(f"EDIT_ID_{ssn}"); top.geometry("450x750"); top.configure(bg=self.colors["bg"]); top.grab_set()
        conn = db.get_db()
        try:
            p = conn.execute("SELECT FirstName, MiddleName, LastName, Address, Gender, DateOfBirth FROM Person WHERE SSN=?", (ssn,)).fetchone()
            ph = conn.execute("SELECT PhoneNumber FROM Person_Phone WHERE SSN=?", (ssn,)).fetchone()
            extra, mem_val = None, None
            if role == "Receptionist": extra = conn.execute("SELECT Shift, Salary FROM Receptionist WHERE SSN=?", (ssn,)).fetchone()
            elif role == "Trainer": extra = conn.execute("SELECT Branch, Salary FROM Trainer WHERE SSN=?", (ssn,)).fetchone()
            elif role == "GymMember": 
                t = conn.execute("SELECT TrainerSSN FROM GymMember WHERE SSN=?", (ssn,)).fetchone()
                extra = t[0] if t else None
                mem_val = conn.execute("SELECT Type, StartDate FROM Membership WHERE MemberSSN=? ORDER BY ID DESC LIMIT 1", (ssn,)).fetchone()
            trainers = conn.execute("SELECT P.FirstName, T.SSN FROM Trainer T JOIN Person P ON T.SSN=P.SSN").fetchall()
        except: conn.close(); return
        finally: conn.close()

        t_map = {n: s for n, s in trainers}; t_map_inv = {s: n for n, s in trainers}
        f = tk.Frame(top, bg=self.colors["bg"], padx=20); f.pack(fill="both", expand=True)
        entries = {}

        def row(r, l, v, k, vals=None):
            tk.Label(f, text=l, bg=self.colors["bg"], fg="white", font=("Consolas", 10)).grid(row=r, column=0, sticky="w", pady=5)
            if vals: e = ttk.Combobox(f, values=vals, state="readonly", width=23); e.set(v) if v else None
            else: e = ttk.Entry(f, width=25); e.insert(0, str(v)) if v else None
            e.grid(row=r, column=1, sticky="ew", padx=10); entries[k] = e

        row(0, "NAME", p[0], "FirstName"); row(1, "MIDDLE", p[1], "MiddleName"); row(2, "SURNAME", p[2], "LastName")
        row(3, "ADDRESS", p[3], "Address"); row(4, "GENDER", p[4], "Gender", ["Male", "Female"]); row(5, "DOB", p[5], "DateOfBirth")
        row(6, "PHONE", ph[0] if ph else "", "Phone")

        cr = 7
        if role in ["Receptionist", "Trainer"]:
            row(cr, "SALARY", extra[1] if extra else 0, "Salary"); cr+=1
            lbl = "SHIFT" if role=="Receptionist" else "BRANCH"
            val = extra[0] if extra else ""
            if role == "Receptionist": row(cr, lbl, val, "Extra", ["Day", "Night"])
            else: row(cr, lbl, val, "Extra")
        elif role == "GymMember":
            tk.Label(f, text="TRAINER", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=cr, column=0, sticky="w")
            cb = ttk.Combobox(f, values=list(t_map.keys()), state="readonly"); cb.grid(row=cr, column=1, sticky="ew", padx=10)
            if extra and extra in t_map_inv: cb.set(t_map_inv[extra])
            entries["Trainer"] = cb; cr+=1
            
            row(cr, "START DATE", mem_val[1] if mem_val else "", "StartDate"); cr+=1
            
            tk.Label(f, text="PACKAGE", bg=self.colors["bg"], fg=self.colors["accent"]).grid(row=cr, column=0, sticky="w")
            cb_p = ttk.Combobox(f, values=list(self.PACKAGES.keys()), state="readonly"); cb_p.grid(row=cr, column=1, sticky="ew", padx=10)
            if mem_val and mem_val[0] in self.PACKAGES: cb_p.set(mem_val[0])
            entries["Package"] = cb_p

        def update():
            try:
                conn = db.get_db()
                conn.execute("UPDATE Person SET FirstName=?, MiddleName=?, LastName=?, Address=?, Gender=?, DateOfBirth=? WHERE SSN=?", 
                             (entries["FirstName"].get(), entries["MiddleName"].get(), entries["LastName"].get(), entries["Address"].get(), entries["Gender"].get(), entries["DateOfBirth"].get(), ssn))
                conn.execute("DELETE FROM Person_Phone WHERE SSN=?", (ssn,))
                if entries["Phone"].get(): conn.execute("INSERT INTO Person_Phone VALUES (?,?)", (ssn, entries["Phone"].get()))

                if role == "Receptionist": conn.execute("UPDATE Receptionist SET Shift=?, Salary=? WHERE SSN=?", (entries["Extra"].get(), entries["Salary"].get(), ssn))
                elif role == "Trainer": conn.execute("UPDATE Trainer SET Branch=?, Salary=? WHERE SSN=?", (entries["Extra"].get(), entries["Salary"].get(), ssn))
                elif role == "GymMember":
                    if entries["Trainer"].get(): conn.execute("UPDATE GymMember SET TrainerSSN=? WHERE SSN=?", (t_map[entries["Trainer"].get()], ssn))
                    pkg, s_date = entries["Package"].get(), entries["StartDate"].get()
                    if pkg and pkg in self.PACKAGES and s_date:
                        s_dt = datetime.strptime(s_date, "%Y-%m-%d")
                        days = self.PACKAGES[pkg]["days"]
                        e_str = (s_dt + timedelta(days=days)).strftime("%Y-%m-%d")
                        conn.execute("UPDATE Membership SET Type=?, Price=?, StartDate=?, EndDate=? WHERE MemberSSN=? AND ID = (SELECT MAX(ID) FROM Membership WHERE MemberSSN=?)", 
                                     (pkg, self.PACKAGES[pkg]["price"], s_date, e_str, ssn, ssn))
                conn.commit(); refresh_callback(); top.destroy(); messagebox.showinfo("SYSTEM", "UPDATE COMPLETE")
            except Exception as e: messagebox.showerror("ERROR", str(e))
            finally: conn.close()
        ttk.Button(top, text="[ UPDATE ]", command=update).pack(pady=20, fill="x", padx=40)

    # --- SHOW DETAILS ---
    def show_person_details(self, ssn, role, refresh_callback):
        conn = db.get_db(); p = conn.execute("SELECT * FROM Person WHERE SSN=?", (ssn,)).fetchone(); ph = conn.execute("SELECT PhoneNumber FROM Person_Phone WHERE SSN=?", (ssn,)).fetchone()
        phone = ph[0] if ph else "N/A"; extra = []
        if role == "Receptionist":
            r = conn.execute("SELECT Shift, Salary, HireDate FROM Receptionist WHERE SSN=?", (ssn,)).fetchone()
            if r: extra = [("SHIFT", r[0]), ("SALARY", f"{r[1]}$"), ("HIRED", r[2])]
        elif role == "Trainer":
            r = conn.execute("SELECT Branch, Salary, HireDate FROM Trainer WHERE SSN=?", (ssn,)).fetchone()
            if r: extra = [("BRANCH", r[0]), ("SALARY", f"{r[1]}$"), ("HIRED", r[2])]
        elif role == "GymMember":
            m = conn.execute("SELECT Type, StartDate, EndDate FROM Membership WHERE MemberSSN=?", (ssn,)).fetchone()
            if m: extra = [("PACKAGE", m[0]), ("VALID", f"{m[1]} -> {m[2]}")]
            else: extra = [("STATUS", "NO PLAN")]
        conn.close()

        top = tk.Toplevel(self.root); top.title("DATA_CARD"); top.geometry("450x650"); top.configure(bg=self.colors["bg"])
        tk.Label(top, text=f"{p[1]} {p[2]} {p[3]}", font=("Consolas", 18, "bold"), bg=self.colors["bg"], fg="white").pack(pady=20)
        tf = tk.Frame(top, bg=self.colors["dark"], padx=2, pady=2); tf.pack(fill="x", padx=20); tf.columnconfigure(1, weight=1)
        
        rows = [("PHONE", phone), ("ADDRESS", p[6]), ("GENDER", p[4]), ("DOB", p[5]), ("---", "---")] + extra
        cr = 0
        for l, v in rows:
            if l == "---": tk.Frame(tf, height=2, bg=self.colors["accent"]).grid(row=cr, column=0, columnspan=2, sticky="ew", pady=10); cr+=1; continue
            tk.Label(tf, text=l, font=("Consolas", 10, "bold"), bg=self.colors["dark"], fg=self.colors["accent"], anchor="w", pady=8, padx=10).grid(row=cr, column=0, sticky="ew")
            tk.Label(tf, text=str(v), font=("Consolas", 10), bg=self.colors["dark"], fg="white", anchor="e", pady=8, padx=10).grid(row=cr, column=1, sticky="ew")
            tk.Frame(tf, height=1, bg="#333").grid(row=cr+1, column=0, columnspan=2, sticky="ew"); cr+=2

        ttk.Button(top, text="[ EDIT ]", command=lambda: (top.destroy(), self.open_edit_popup(ssn, role, refresh_callback))).pack(pady=20, fill="x", padx=40)

    def setup_hr(self, tab, table):
        p = self.tabs[tab]; top = tk.Frame(p, bg=self.colors["bg"], pady=10); top.pack(fill="x", padx=10)
        tf = tk.Frame(p, bg=self.colors["bg"]); tf.pack(fill="both", expand=True, padx=10, pady=5)
        ec = "SHIFT" if table == "Receptionist" else "BRANCH"
        cols = ("SSN", "NAME", "MIDDLE", "SURNAME", "GENDER", "DOB", "ADDRESS", "PHONE", "SALARY", ec)
        tree = ttk.Treeview(tf, columns=cols, show="headings"); ysb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview); xsb = ttk.Scrollbar(tf, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set); tree.grid(row=0, column=0, sticky="nsew"); ysb.grid(row=0, column=1, sticky="ns"); xsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1); tf.grid_columnconfigure(0, weight=1)
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center", width=90)

        def ref():
            for i in tree.get_children(): tree.delete(i)
            conn = db.get_db(); db_col = "Shift" if table == "Receptionist" else "Branch"
            q = f"SELECT P.SSN, P.FirstName, P.MiddleName, P.LastName, P.Gender, P.DateOfBirth, P.Address, PH.PhoneNumber, R.Salary, R.{db_col} FROM {table} R JOIN Person P ON R.SSN=P.SSN LEFT JOIN Person_Phone PH ON P.SSN=PH.SSN"
            for r in conn.execute(q): tree.insert("", "end", values=[str(x) if x else "" for x in r])
            conn.close()
        
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("CONFIRM", "Delete?"):
                ssn = tree.item(sel)['values'][0]; conn = db.get_db()
                for t in [table, "Person_Phone", "Person"]: conn.execute(f"DELETE FROM {t} WHERE SSN=?", (ssn,))
                conn.commit(); conn.close(); ref()
        
        ttk.Button(top, text="[ ADD + ]", command=lambda: self.open_add_person_popup(table, ref)).pack(side="left")
        ttk.Button(top, text="[ DELETE - ]", style="Danger.TButton", command=delete).pack(side="right")
        tree.bind("<Double-1>", lambda e: self.show_person_details(tree.item(tree.selection())['values'][0], table, ref)); ref()

    def setup_student_control(self):
        p = self.tabs["GYM MEMBER"]; top = tk.Frame(p, bg=self.colors["bg"], pady=10); top.pack(fill="x", padx=20)
        tf = tk.Frame(p, bg=self.colors["bg"]); tf.pack(fill="both", expand=True, padx=20, pady=5)
        cols = ("SSN", "NAME", "MIDDLE", "SURNAME", "GENDER", "DOB", "ADDRESS", "PHONE", "TRAINER", "PACKAGE", "START", "END")
        tree = ttk.Treeview(tf, columns=cols, show="headings"); ysb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview); xsb = ttk.Scrollbar(tf, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set); tree.grid(row=0, column=0, sticky="nsew"); ysb.grid(row=0, column=1, sticky="ns"); xsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1); tf.grid_columnconfigure(0, weight=1)
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center", width=85)

        def ref():
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

        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno("CONFIRM", "Delete member?"):
                ssn = tree.item(sel)['values'][0]; conn=db.get_db()
                for t in ["Membership", "GymMember", "Person_Phone", "Person"]: 
                    try: conn.execute(f"DELETE FROM {t} WHERE {'MemberSSN' if t=='Membership' else 'SSN'}=?", (ssn,))
                    except: pass
                conn.commit(); conn.close(); ref()

        ttk.Button(top, text="[ ADD + ]", command=lambda: self.open_add_student_popup(ref)).pack(side="left")
        ttk.Button(top, text="[ DELETE - ]", style="Danger.TButton", command=delete).pack(side="right")
        tree.bind("<Double-1>", lambda e: self.show_person_details(tree.item(tree.selection())['values'][0], "GymMember", ref)); ref()

    def setup_equipment(self):
        p = self.tabs["EQUIPMENT INVENTORY"]; f = tk.LabelFrame(p, text="// INVENTORY", bg=self.colors["bg"], fg=self.colors["accent"], font=("Consolas", 10, "bold"), padx=15, pady=15); f.pack(fill="x", padx=10, pady=10)
        tk.Label(f, text="ITEM NAME:", bg=self.colors["bg"], fg="white").pack(side="left"); e1=ttk.Entry(f); e1.pack(side="left", padx=10)
        tk.Label(f, text="TYPE:", bg=self.colors["bg"], fg="white").pack(side="left"); e2=ttk.Entry(f); e2.pack(side="left", padx=10)
        tree = ttk.Treeview(p, columns=("ID", "NAME", "TYPE"), show="headings"); [tree.heading(c, text=c) for c in tree['columns']]; tree.pack(fill="both", expand=True, padx=10)
        def ref():
            for i in tree.get_children(): tree.delete(i)
            conn=db.get_db(); [tree.insert("", "end", values=r) for r in conn.execute("SELECT * FROM Equipment")]; conn.close()
        def add(): conn=db.get_db(); conn.execute("INSERT INTO Equipment (Name, Type) VALUES (?,?)", (e1.get(), e2.get())); conn.commit(); conn.close(); ref()
        def dele(): 
            sel=tree.selection(); 
            if sel: conn=db.get_db(); conn.execute("DELETE FROM Equipment WHERE ID=?", (tree.item(sel)['values'][0],)); conn.commit(); conn.close(); ref()
        ttk.Button(f, text="[ ADD ]", command=add).pack(side="left", padx=10); ttk.Button(p, text="[ DELETE ]", style="Danger.TButton", command=dele).pack(pady=10); ref()