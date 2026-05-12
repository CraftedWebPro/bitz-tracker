import tkinter as tk
from tkinter import ttk, messagebox
from lib import config
from lib.utils.profile import load, save

BG = config.COLORS["bg"]
CARD = config.COLORS["card"]
BORDER = config.COLORS["border"]
ACCENT = config.COLORS["accent"]
TEXT = config.COLORS["text"]
TEXT2 = config.COLORS["text2"]
FONT = "Segoe UI"


class Btn(tk.Label):
    def __init__(self, parent, text, cmd, bg=CARD, fg=TEXT, hbg=BORDER, hfg=TEXT,
                 bold=False, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=(FONT, 10, "bold" if bold else "normal"),
                         cursor="hand2", padx=18, pady=9, **kw)
        self._bg, self._fg, self._hbg, self._hfg = bg, fg, hbg, hfg
        self.bind("<Enter>", lambda _: self.config(bg=self._hbg, fg=self._hfg))
        self.bind("<Leave>", lambda _: self.config(bg=self._bg, fg=self._fg))
        self.bind("<Button-1>", lambda _: cmd())


class ProfileDialog:
    W, H = 420, 500

    FIELDS = [
        ("name",             "Your Name"),
        ("profession",       "Profession (lowercase)"),
        ("profession_title", "Profession Title (capitalized)"),
        ("location",         "Location"),
        ("website",          "Website URL"),
    ]

    def __init__(self, parent):
        self.parent = parent
        self.profile = load()

        self.win = tk.Toplevel(parent)
        self.win.title("Profile Settings")
        self.win.configure(bg=BG)
        self.win.resizable(True, True)
        self.win.minsize(400, 420)

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+"
                          f"{(sw - self.W) // 2}+{(sh - self.H) // 2}")

        self._build()

    def _build(self):
        # ── Header ──
        hf = tk.Frame(self.win, bg=CARD, height=60)
        hf.pack(fill="x")
        hf.pack_propagate(False)

        stripe = tk.Frame(hf, bg=ACCENT, height=3)
        stripe.pack(fill="x")

        row = tk.Frame(hf, bg=CARD)
        row.pack(fill="x", padx=20, pady=(8, 0))

        tk.Label(row, text="Profile Settings",
                 font=(FONT, 13, "bold"), bg=CARD, fg=TEXT).pack(side="left")

        tk.Label(hf, text="Your details used in WhatsApp messages",
                 font=(FONT, 9), bg=CARD, fg=TEXT2).pack(anchor="w", padx=20)

        # ── Body (scrollable area) ──
        body = tk.Frame(self.win, bg=BG)
        body.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview,
                                 bg=BORDER, troughcolor=BG, width=8)
        form_frame = tk.Frame(canvas, bg=BG)

        form_frame.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._inner = canvas.create_window(
            (0, 0), window=form_frame, anchor="nw")

        def _reconfigure(event):
            canvas.itemconfig(self._inner, width=event.width)
        canvas.bind("<Configure>", _reconfigure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, pady=(12, 0))
        scrollbar.pack(side="right", fill="y", pady=(12, 0))

        def _mw(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self.win.bind("<MouseWheel>", _mw, add="+")

        # ── Form fields ──
        self.entries = {}
        for key, label in self.FIELDS:
            f = tk.Frame(form_frame, bg=BG)
            f.pack(fill="x", pady=(0, 10))

            tk.Label(f, text=label, bg=BG, fg=TEXT2,
                     font=(FONT, 9)).pack(anchor="w")

            e = tk.Entry(f, bg=CARD, fg=TEXT, insertbackground=TEXT,
                         relief="flat", font=(FONT, 10),
                         highlightbackground=BORDER, highlightthickness=1)
            e.pack(fill="x", ipady=6, pady=(2, 0))
            e.insert(0, self.profile.get(key, ""))
            self.entries[key] = e

        tk.Label(form_frame, text="These will appear in message intros and signatures.",
                 bg=BG, fg=TEXT2, font=(FONT, 7)).pack(anchor="w", pady=(0, 4))

        # ── Buttons at bottom ──
        btn_row = tk.Frame(self.win, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 12))

        Btn(btn_row, "Cancel", self.win.destroy).pack(side="left")
        Btn(btn_row, "Save", self.save, bg=ACCENT, fg="#fff",
            hbg=BORDER, hfg="#fff", bold=True).pack(side="right")

    def save(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        try:
            save(data)
            messagebox.showinfo("Saved", "Profile updated!", parent=self.win)
            self.win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.win)
