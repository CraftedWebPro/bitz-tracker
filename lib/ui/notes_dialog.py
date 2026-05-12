import tkinter as tk
from tkinter import ttk, messagebox
from lib import config

class _HoverButton(tk.Label):
    """Flat label that behaves like a button with hover colour."""
    def __init__(self, parent, text, command, bg=config.COLORS["card"], fg=config.COLORS["text"],
                 hover_bg=config.COLORS["border"], font=("Segoe UI", 10, "bold"), **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         cursor="hand2", padx=18, pady=9, **kw)
        self._bg, self._hbg, self._cmd = bg, hover_bg, command
        self.bind("<Enter>",  lambda _: self.config(bg=self._hbg))
        self.bind("<Leave>",  lambda _: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda _: self._cmd())

class NotesDialog:
    W, H = 450, 320

    def __init__(self, parent, controller, businesses):
        self.parent = parent
        self.controller = controller
        self.businesses = businesses
        
        self.win = tk.Toplevel(parent)
        self.win.title("Add Notes")
        self.win.geometry(f"{self.W}x{self.H}")
        self.win.configure(bg=config.COLORS["bg"])
        self.win.resizable(False, False)
        
        # Center window
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")
        
        self._build()

    def _build(self):
        self._header()
        self._body()

    def _header(self):
        hf = tk.Frame(self.win, bg=config.COLORS["card"], height=70)
        hf.pack(fill="x")
        hf.pack_propagate(False)
        
        # Accent stripe
        stripe = tk.Frame(hf, bg=config.COLORS["accent"], height=3)
        stripe.pack(fill="x")
        
        row = tk.Frame(hf, bg=config.COLORS["card"])
        row.pack(fill="x", padx=20, pady=(10, 0))
        
        # Icon
        ic = tk.Canvas(row, width=26, height=26, bg=config.COLORS["card"],
                       highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        ic.create_oval(3, 3, 23, 23, fill=config.COLORS["border"], outline=config.COLORS["accent"], width=1.5)
        ic.create_text(13, 13, text="N", fill=config.COLORS["accent"], font=("Segoe UI", 12, "bold"))
        
        tk.Label(row, text="Add Notes", font=("Segoe UI", 13, "bold"),
                 bg=config.COLORS["card"], fg=config.COLORS["text"]).pack(side="left")
        
        tk.Label(hf, text=f"Updating {len(self.businesses)} business{'es' if len(self.businesses)!=1 else ''}",
                 font=("Segoe UI", 9), bg=config.COLORS["card"], fg=config.COLORS["text2"]).pack(
                 anchor="w", padx=20)

    def _body(self):
        body = tk.Frame(self.win, bg=config.COLORS["bg"])
        body.pack(fill="both", expand=True, padx=25, pady=20)
        
        tk.Label(body, text="BUSINESS NOTES",
                 font=("Segoe UI", 8, "bold"),
                 bg=config.COLORS["bg"], fg=config.COLORS["text3"]).pack(anchor="w", pady=(0, 5))
        
        self.notes_text = tk.Text(body, height=6, font=("Segoe UI", 11),
                                  bg=config.COLORS["card"], fg=config.COLORS["text"],
                                  insertbackground=config.COLORS["text"],
                                  relief="flat", padx=12, pady=12,
                                  highlightbackground=config.COLORS["border"], highlightthickness=1)
        self.notes_text.pack(fill="x", pady=(0, 20))
        
        # Pre-fill notes if only one business selected
        if len(self.businesses) == 1:
            current_notes = self.businesses[0].get("Notes", "") or ""
            self.notes_text.insert("1.0", current_notes)
        
        btn_row = tk.Frame(body, bg=config.COLORS["bg"])
        btn_row.pack(fill="x")
        
        cancel_btn = _HoverButton(btn_row, "Cancel",
                                   command=self.win.destroy,
                                   bg=config.COLORS["card"], hover_bg=config.COLORS["border"],
                                   fg=config.COLORS["text2"], font=("Segoe UI", 10))
        cancel_btn.pack(side="left")
        
        save_btn = _HoverButton(btn_row, "Save Notes",
                                command=self.save,
                                bg=config.COLORS["accent"], hover_bg=config.COLORS["border"],
                                fg=config.COLORS["white"], font=("Segoe UI", 10, "bold"))
        save_btn.pack(side="right")

    def save(self):
        new_notes = self.notes_text.get("1.0", "end").strip()
        wb_write = self.controller.get_writable_wb()
        ws_write = wb_write.active
        
        from lib.utils.excel_func import update_row_in_excel
        for biz in self.businesses:
            old_notes = biz.get("Notes", "") or ""
            if old_notes and new_notes:
                combined = f"{old_notes} | {new_notes}"
            else:
                combined = old_notes or new_notes
            update_row_in_excel(wb_write, ws_write, config.EXCEL_PATH, biz, Notes=combined)
        
        self.controller.refresh()
        self.win.destroy()

