import tkinter as tk
from tkinter import ttk

# --- COLORS ---
CYBER_BLACK = "#050a0e"    # Bg
CYBER_DARK  = "#121b22"    # Panels
NEON_CYAN   = "#00f3ff"    # Accents
NEON_PINK   = "#ff003c"    # Danger
TEXT_MAIN   = "#e0e6ed"    # Text

FONT_HEADER = ("Consolas", 16, "bold")
FONT_BODY   = ("Segoe UI", 10)

class CyberpunkTheme:
    @staticmethod
    def apply_theme(root):
        root.configure(bg=CYBER_BLACK)
        
        # Combobox fix
        root.option_add('*TCombobox*Listbox.background', CYBER_DARK)
        root.option_add('*TCombobox*Listbox.foreground', TEXT_MAIN)
        root.option_add('*TCombobox*Listbox.selectBackground', NEON_CYAN)
        root.option_add('*TCombobox*Listbox.selectForeground', 'black')
        
        style = ttk.Style()
        try: style.theme_use('clam') 
        except: pass

        # General
        style.configure(".", background=CYBER_BLACK, foreground=TEXT_MAIN, font=FONT_BODY, borderwidth=0)
        style.configure("TFrame", background=CYBER_BLACK)
        style.configure("TLabel", background=CYBER_BLACK, foreground=TEXT_MAIN)
        style.configure("TLabelframe", background=CYBER_BLACK, foreground=NEON_CYAN, bordercolor=NEON_CYAN)
        style.configure("TLabelframe.Label", background=CYBER_BLACK, foreground=NEON_CYAN, font=("Consolas", 11, "bold"))

        # Buttons
        style.configure("TButton", font=("Consolas", 11, "bold"), padding=(12,10), background=CYBER_DARK, foreground=NEON_CYAN, borderwidth=1, relief="flat", focuscolor=NEON_CYAN, bordercolor=NEON_CYAN, anchor="center")
        style.map("TButton", background=[("active", NEON_CYAN), ("pressed", NEON_CYAN)], foreground=[("active", "black"), ("pressed", "black")])

        style.configure("Danger.TButton", foreground=NEON_PINK, bordercolor=NEON_PINK)
        style.map("Danger.TButton", background=[("active", NEON_PINK)], foreground=[("active", "black")])

        # Inputs
        style.configure("TEntry", fieldbackground=CYBER_DARK, foreground="white", insertcolor=NEON_CYAN, bordercolor=NEON_CYAN)
        style.configure("TCombobox", fieldbackground=CYBER_DARK, background=CYBER_DARK, foreground="white", arrowcolor=NEON_CYAN, bordercolor=NEON_CYAN)
        style.map("TCombobox", fieldbackground=[("readonly", CYBER_DARK)])

        # Treeview
        style.configure("Treeview", background=CYBER_DARK, fieldbackground=CYBER_DARK, foreground=TEXT_MAIN, rowheight=35, font=FONT_BODY, borderwidth=0)
        style.configure("Treeview.Heading", background="black", foreground=NEON_CYAN, font=("Consolas", 11, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", NEON_CYAN)], foreground=[("selected", "black")])

        # Notebook
        style.configure("TNotebook", background=CYBER_BLACK, borderwidth=0)
        style.configure("TNotebook.Tab", background=CYBER_BLACK, foreground="#8b9bb4", padding=[15, 8], font=("Consolas", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", CYBER_DARK)], foreground=[("selected", NEON_CYAN)])

    @staticmethod
    def get_colors():
        return {"bg": CYBER_BLACK, "fg": TEXT_MAIN, "accent": NEON_CYAN, "danger": NEON_PINK, "dark": CYBER_DARK}

    @staticmethod
    def center_window(root, width=400, height=500):
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")