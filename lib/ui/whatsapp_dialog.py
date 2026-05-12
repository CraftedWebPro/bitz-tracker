# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import time
from lib import config
from lib.utils.message_templates import SECTIONS, generate_message
from lib.utils.actions import open_whatsapp_send


# ── Palette (mirrors lead_finder.py) ─────────────────────────────────────────
BG        = "#0f0f13"
SURFACE   = "#1a1a24"
BORDER    = "#2a2a3a"
ACCENT    = "#25D366"          # WhatsApp green (replaces Google blue)
ACCENT_HV = "#1aab50"
ACCENT2   = "#128C7E"          # WA dark-green for "Send All"
TEXT      = "#e8e8f0"
MUTED     = "#7a7a95"
TEXT2     = "#b0b0c8"
WA_GREEN  = "#25D366"


# ── Reusable widgets ──────────────────────────────────────────────────────────

class _HoverButton(tk.Label):
    """Flat label that behaves like a button with hover colour."""
    def __init__(self, parent, text, command,
                 bg=ACCENT, fg=TEXT, hover_bg=ACCENT_HV,
                 font=("Segoe UI", 10, "bold"), **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         cursor="hand2", padx=18, pady=9, **kw)
        self._bg, self._hbg, self._cmd = bg, hover_bg, command
        self.bind("<Enter>",  lambda _: self.config(bg=self._hbg))
        self.bind("<Leave>",  lambda _: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda _: self._cmd())


class _StyledCombo(ttk.Combobox):
    """Dark-themed combobox — style is initialised once."""
    _style_init = False

    def __init__(self, parent, **kw):
        if not _StyledCombo._style_init:
            s = ttk.Style()
            s.theme_use("clam")
            s.configure("Dark.TCombobox",
                        fieldbackground=SURFACE,
                        background=SURFACE,
                        foreground=TEXT,
                        selectbackground=ACCENT,
                        selectforeground="#000",
                        bordercolor=BORDER,
                        arrowcolor=MUTED,
                        relief="flat",
                        padding=(8, 6))
            s.map("Dark.TCombobox",
                  fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)],
                  bordercolor=[("focus", ACCENT)])
            _StyledCombo._style_init = True
        super().__init__(parent, style="Dark.TCombobox",
                         font=("Segoe UI", 10), state="readonly", **kw)


class _Card(tk.Frame):
    """Surface-coloured card with a subtle border stripe on the left."""
    def __init__(self, parent, accent_bar=False, **kw):
        super().__init__(parent, bg=SURFACE, **kw)
        if accent_bar:
            bar = tk.Frame(self, bg=ACCENT, width=3)
            bar.pack(side="left", fill="y")


class _SectionLabel(tk.Label):
    def __init__(self, parent, text, **kw):
        super().__init__(parent, text=text.upper(),
                         font=("Segoe UI", 8, "bold"),
                         bg=SURFACE, fg=MUTED, **kw)


class _DarkCheck(tk.Checkbutton):
    """Checkbutton styled for the dark theme."""
    def __init__(self, parent, **kw):
        super().__init__(parent,
                         bg=SURFACE, fg=TEXT,
                         selectcolor="#0f0f13",
                         activebackground=SURFACE,
                         activeforeground=TEXT,
                         font=("Segoe UI", 9),
                         relief="flat",
                         **kw)


# ── Main dialog ───────────────────────────────────────────────────────────────

class WhatsAppDialog:
    W, H = 720, 680

    def __init__(self, parent, controller, businesses):
        self.parent     = parent
        self.controller = controller
        self.businesses = businesses

        self.win = tk.Toplevel(parent)
        self.win.title("WhatsApp Message Preview")
        self.win.configure(bg=BG)
        self.win.resizable(True, True)
        self.win.minsize(600, 560)

        # Centre on screen
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+"
                          f"{(sw - self.W) // 2}+{(sh - self.H) // 2}")

        # State
        self.current_idx      = tk.IntVar(value=0)
        self.tone_var         = tk.StringVar(value="friendly")
        self.no_website_var   = tk.BooleanVar(value=False)
        self.sections_vars    = {s: tk.BooleanVar(value=True) for s in SECTIONS}

        self._build()
        self.update_review()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self._header()
        self._footer()          # pack footer before content so it sticks to bottom
        self._content()

    # ── Header ───────────────────────────────────────────────────────────────

    def _header(self):
        hf = tk.Frame(self.win, bg=SURFACE, height=68)
        hf.pack(side="top", fill="x")
        hf.pack_propagate(False)

        # WhatsApp-coloured top stripe
        stripe = tk.Canvas(hf, height=3, bg=SURFACE, highlightthickness=0)
        stripe.pack(fill="x")
        stripe.update_idletasks()
        stripe.create_rectangle(0, 0, 10_000, 3, fill=WA_GREEN, outline="")

        row = tk.Frame(hf, bg=SURFACE)
        row.pack(fill="x", padx=20, pady=(6, 0))

        # WhatsApp icon (simple canvas bubble)
        ic = tk.Canvas(row, width=28, height=28, bg=SURFACE, highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        ic.create_oval(2, 2, 26, 26, fill="#1a3a2a", outline=WA_GREEN, width=1.5)
        # speech-bubble dot
        ic.create_oval(10, 11, 18, 19, fill=WA_GREEN, outline="")

        tk.Label(row, text="WhatsApp Message Preview",
                 font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side="left")

        count_badge = tk.Label(row,
                               text=f" {len(self.businesses)} selected ",
                               font=("Segoe UI", 8, "bold"),
                               bg=WA_GREEN, fg="#000",
                               padx=6, pady=2)
        count_badge.pack(side="left", padx=10)

        tk.Label(hf, text="Compose & preview outreach messages",
                 font=("Segoe UI", 9), bg=SURFACE, fg=MUTED).pack(
                 anchor="w", padx=20)

    # ── Footer button bar ─────────────────────────────────────────────────────

    def _footer(self):
        bar = tk.Frame(self.win, bg=SURFACE, height=64)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        # thin top divider
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x")

        btn_row = tk.Frame(bar, bg=SURFACE)
        btn_row.pack(fill="x", padx=20, pady=12)

        _HoverButton(btn_row, "✉  Send This",
                     command=self.send_current,
                     bg=ACCENT, hover_bg=ACCENT_HV,
                     fg="#000", font=("Segoe UI", 10, "bold")
                     ).pack(side="left", padx=(0, 8))

        if len(self.businesses) > 1:
            _HoverButton(btn_row, "⟳  Send All One-by-One",
                         command=self.send_all,
                         bg=ACCENT2, hover_bg="#0e6b5e",
                         fg="#fff", font=("Segoe UI", 10, "bold")
                         ).pack(side="left", padx=(0, 8))

        _HoverButton(btn_row, "Close",
                     command=self.win.destroy,
                     bg="#23232f", hover_bg="#2e2e3f",
                     fg=MUTED, font=("Segoe UI", 10)
                     ).pack(side="right")

    # ── Main content ──────────────────────────────────────────────────────────

    def _content(self):
        outer = tk.Frame(self.win, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        # Two-column layout: left = options, right = preview
        left  = tk.Frame(outer, bg=BG, width=220)
        right = tk.Frame(outer, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 12))
        right.pack(side="left", fill="both", expand=True)
        left.pack_propagate(False)

        self._options_panel(left)
        self._preview_panel(right)

    # ── Options panel (left column) ───────────────────────────────────────────

    def _options_panel(self, parent):
        # ── Navigation card ──────────────────────────────────────────────────
        if len(self.businesses) > 1:
            nav_card = _Card(parent, accent_bar=True)
            nav_card.pack(fill="x", pady=(0, 8))

            inner = tk.Frame(nav_card, bg=SURFACE)
            inner.pack(fill="x", padx=10, pady=10)

            _SectionLabel(inner, "Navigate").pack(anchor="w", pady=(0, 6))

            nav_btn_row = tk.Frame(inner, bg=SURFACE)
            nav_btn_row.pack(fill="x")

            _HoverButton(nav_btn_row, "‹ Prev",
                         command=self.go_prev,
                         bg="#23232f", hover_bg="#2e2e3f",
                         fg=TEXT, font=("Segoe UI", 9)
                         ).pack(side="left", padx=(0, 4))

            _HoverButton(nav_btn_row, "Next ›",
                         command=self.go_next,
                         bg="#23232f", hover_bg="#2e2e3f",
                         fg=TEXT, font=("Segoe UI", 9)
                         ).pack(side="left")

            self.nav_label = tk.Label(inner, text="",
                                      bg=SURFACE, fg=MUTED,
                                      font=("Segoe UI", 8))
            self.nav_label.pack(anchor="w", pady=(6, 0))

        # ── Tone card ────────────────────────────────────────────────────────
        tone_card = _Card(parent, accent_bar=True)
        tone_card.pack(fill="x", pady=(0, 8))

        tone_inner = tk.Frame(tone_card, bg=SURFACE)
        tone_inner.pack(fill="x", padx=10, pady=10)

        _SectionLabel(tone_inner, "Message Tone").pack(anchor="w", pady=(0, 6))

        combo = _StyledCombo(tone_inner,
                             textvariable=self.tone_var,
                             values=["friendly", "professional", "urgent"],
                             width=20)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", lambda _: self.update_review())

        # ── Options card ─────────────────────────────────────────────────────
        opt_card = _Card(parent, accent_bar=True)
        opt_card.pack(fill="x", pady=(0, 8))

        opt_inner = tk.Frame(opt_card, bg=SURFACE)
        opt_inner.pack(fill="x", padx=10, pady=10)

        _SectionLabel(opt_inner, "Options").pack(anchor="w", pady=(0, 6))

        _DarkCheck(opt_inner, text="No website",
                   variable=self.no_website_var,
                   command=self.update_review).pack(anchor="w")

        # ── Sections card ────────────────────────────────────────────────────
        sec_card = _Card(parent, accent_bar=True)
        sec_card.pack(fill="x", pady=(0, 8))

        sec_inner = tk.Frame(sec_card, bg=SURFACE)
        sec_inner.pack(fill="x", padx=10, pady=10)

        _SectionLabel(sec_inner, "Include Sections").pack(anchor="w", pady=(0, 6))

        for s in SECTIONS:
            _DarkCheck(sec_inner,
                       text=s.replace("_", " ").title(),
                       variable=self.sections_vars[s],
                       command=self.update_review).pack(anchor="w", pady=2)

    # ── Preview panel (right column) ──────────────────────────────────────────

    def _preview_panel(self, parent):
        # Info bar
        info_bar = tk.Frame(parent, bg=BG)
        info_bar.pack(fill="x", pady=(0, 8))

        tk.Label(info_bar, text="MESSAGE PREVIEW",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(side="left")

        self.info_label = tk.Label(info_bar, text="",
                                   font=("Segoe UI", 8),
                                   bg=BG, fg=TEXT2)
        self.info_label.pack(side="right")

        # Preview card
        preview_card = tk.Frame(parent, bg=SURFACE,
                                highlightbackground=BORDER,
                                highlightthickness=1)
        preview_card.pack(fill="both", expand=True)

        # thin green top accent on the preview card
        tk.Frame(preview_card, bg=WA_GREEN, height=2).pack(fill="x")

        # scrollable text
        scroll_frame = tk.Frame(preview_card, bg=SURFACE)
        scroll_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical",
                                 bg=SURFACE, troughcolor=BG,
                                 relief="flat", width=10)

        self.prev_text = tk.Text(scroll_frame,
                                  font=("Segoe UI", 10),
                                  bg=SURFACE, fg=TEXT,
                                  wrap="word", relief="flat",
                                  padx=16, pady=14,
                                  insertbackground=ACCENT,
                                  selectbackground=ACCENT,
                                  selectforeground="#000",
                                  yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.prev_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.prev_text.pack(side="left", fill="both", expand=True)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def go_prev(self):
        self.current_idx.set(max(0, self.current_idx.get() - 1))
        self.update_review()

    def go_next(self):
        self.current_idx.set(min(len(self.businesses) - 1,
                                 self.current_idx.get() + 1))
        self.update_review()

    def update_review(self):
        idx = self.current_idx.get()
        if idx >= len(self.businesses):
            return

        biz      = self.businesses[idx]
        biz_type = biz.get("Type", "Other") or "Other"
        name     = biz.get("Business Name", "")
        website  = biz.get("Website", "")
        phone    = str(biz.get("Phone No", ""))

        is_no_website = self.no_website_var.get() or not str(website).strip()

        msg = generate_message(
            biz_type=biz_type,
            tone=self.tone_var.get(),
            biz_name=name,
            no_website=is_no_website,
            sections=[s for s in SECTIONS if self.sections_vars[s].get()]
        )

        self.prev_text.delete("1.0", "end")
        self.prev_text.insert("1.0", msg)
        self.prev_text.see("1.0")

        self.info_label.config(
            text=f"{name}  ·  {biz_type}  ·  {phone}")

        if len(self.businesses) > 1 and hasattr(self, "nav_label"):
            self.nav_label.config(
                text=f"Showing {idx + 1} of {len(self.businesses)}")

    def send_current(self):
        idx = self.current_idx.get()
        if idx >= len(self.businesses):
            return

        biz           = self.businesses[idx]
        name          = str(biz.get("Business Name", ""))
        website       = biz.get("Website", "")
        is_no_website = self.no_website_var.get() or not str(website).strip()

        msg = generate_message(
            biz_type=biz.get("Type", "Other") or "Other",
            tone=self.tone_var.get(),
            biz_name=name,
            no_website=is_no_website,
            sections=[s for s in SECTIONS if self.sections_vars[s].get()]
        )

        open_whatsapp_send(biz.get("Phone No", ""), name, msg)

        if messagebox.askyesno("Mark Sent",
                                f"Did you send the message to {name}?",
                                parent=self.win):
            self.controller.mark_businesses_sent([biz])

        messagebox.showinfo("Done",
                            f"Process completed for {name}",
                            parent=self.win)

    def send_all(self):
        count = len(self.businesses)
        if not messagebox.askyesno(
                "Confirm",
                f"Open wa.me links for {count} businesses, one by one?\n\n"
                "Each opens in a new browser tab — click Send on each.",
                parent=self.win):
            return

        sent_count = 0
        for biz in self.businesses:
            name          = str(biz.get("Business Name", ""))
            website       = biz.get("Website", "")
            is_no_website = self.no_website_var.get() or not str(website).strip()

            msg = generate_message(
                biz_type=biz.get("Type", "Other") or "Other",
                tone=self.tone_var.get(),
                biz_name=name,
                no_website=is_no_website,
                sections=[s for s in SECTIONS if self.sections_vars[s].get()]
            )

            open_whatsapp_send(biz.get("Phone No", ""), name, msg)
            sent_count += 1
            if sent_count < count:
                time.sleep(2)

        if messagebox.askyesno(
                "Mark Sent",
                f"Opened {sent_count} tabs.\n"
                "Mark all these businesses as Sent in Excel?",
                parent=self.win):
            self.controller.mark_businesses_sent(self.businesses)

        messagebox.showinfo("Done",
                            f"Opened WhatsApp for {sent_count} businesses",
                            parent=self.win)