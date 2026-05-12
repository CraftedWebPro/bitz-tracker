import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import time
from lib.utils.followup_templates import SECTIONS, generate_followup_message
from lib.utils.actions import open_whatsapp_send
from lib.utils.excel_func import update_row_in_excel
from lib import config

# ── Palette (mirrors whatsapp_dialog.py) ────────────────────────────────────────
BG        = "#0f0f13"
SURFACE   = "#1a1a24"
BORDER    = "#2a2a3a"
ACCENT    = "#25D366"
ACCENT_HV = "#1aab50"
ACCENT2   = "#128C7E"
TEXT      = "#e8e8f0"
MUTED     = "#7a7a95"
TEXT2     = "#b0b0c8"
WA_GREEN  = "#25D366"


class _HoverButton(tk.Label):
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
    _style_init = False

    def __init__(self, parent, **kw):
        if not _StyledCombo._style_init:
            s = ttk.Style()
            s.theme_use("clam")
            s.configure("FUDark.TCombobox",
                        fieldbackground=SURFACE,
                        background=SURFACE,
                        foreground=TEXT,
                        selectbackground=ACCENT,
                        selectforeground="#000",
                        bordercolor=BORDER,
                        arrowcolor=MUTED,
                        relief="flat",
                        padding=(8, 6))
            s.map("FUDark.TCombobox",
                  fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)],
                  bordercolor=[("focus", ACCENT)])
            _StyledCombo._style_init = True
        super().__init__(parent, style="FUDark.TCombobox",
                         font=("Segoe UI", 10), state="readonly", **kw)


class _Card(tk.Frame):
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
    def __init__(self, parent, **kw):
        super().__init__(parent,
                         bg=SURFACE, fg=TEXT,
                         selectcolor="#0f0f13",
                         activebackground=SURFACE,
                         activeforeground=TEXT,
                         font=("Segoe UI", 9),
                         relief="flat", **kw)


# ── Main Follow-up Dialog ───────────────────────────────────────────────────────

class FollowUpDialog:
    W, H = 720, 680

    def __init__(self, parent, controller, businesses):
        self.parent     = parent
        self.controller = controller
        self.all_businesses = businesses

        # Filter to businesses eligible for follow-up
        self.businesses = self._filter_eligible(businesses)

        if not self.businesses:
            messagebox.showinfo(
                "No Follow-ups Needed",
                "None of the selected businesses need a follow-up.\n\n"
                "A follow-up can only be sent to businesses that:\n"
                "  - Have been messaged (Msg Sent? = yes)\n"
                "  - Have not replied yet (Reply Came? ≠ yes)\n"
                "  - Haven't had a follow-up sent yet",
                parent=parent)
            self.win = None
            return

        self.win = tk.Toplevel(parent)
        self.win.title("Follow-up Messages")
        self.win.configure(bg=BG)
        self.win.resizable(True, True)
        self.win.minsize(600, 560)

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+"
                          f"{(sw - self.W) // 2}+{(sh - self.H) // 2}")

        # State
        self.current_idx      = tk.IntVar(value=0)
        self.tone_var         = tk.StringVar(value="friendly")
        self.followup_days    = tk.IntVar(value=2)
        self.sections_vars    = {s: tk.BooleanVar(value=True) for s in SECTIONS}

        self._build()
        self.update_review()

    def _filter_eligible(self, businesses):
        eligible = []
        skipped = []
        for b in businesses:
            msg_sent = str(b.get("Msg Sent?", "")).strip().lower()
            reply    = str(b.get("Reply Came?", "")).strip().lower()
            follow   = str(b.get("Follow Up Sent?", "")).strip().lower()
            if msg_sent in ["yes", "y"] and reply not in ["yes", "y"] and follow not in ["yes", "y"]:
                eligible.append(b)
            else:
                skipped.append(b)
        # If there are skipped ones but eligible exist, warn once
        if skipped and eligible:
            self._warn_skipped = skipped
        else:
            self._warn_skipped = []
        return eligible

    def _build(self):
        self._header()
        self._footer()
        self._content()
        # Show a badge about skipped if any
        if getattr(self, "_warn_skipped", None):
            self._show_skipped_badge()

    def _show_skipped_badge(self):
        count = len(self._warn_skipped)
        badge = tk.Frame(self.win, bg="#3a2a00")
        badge.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(badge,
                 text=f"  {count} selected business(es) skipped (not eligible for follow-up)",
                 bg="#3a2a00", fg="#f0c040",
                 font=("Segoe UI", 8)).pack(pady=4)

    def _header(self):
        hf = tk.Frame(self.win, bg=SURFACE, height=68)
        hf.pack(side="top", fill="x")
        hf.pack_propagate(False)

        stripe = tk.Canvas(hf, height=3, bg=SURFACE, highlightthickness=0)
        stripe.pack(fill="x")
        stripe.update_idletasks()
        stripe.create_rectangle(0, 0, 10_000, 3, fill=ACCENT2, outline="")

        row = tk.Frame(hf, bg=SURFACE)
        row.pack(fill="x", padx=20, pady=(6, 0))

        ic = tk.Canvas(row, width=28, height=28, bg=SURFACE, highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        ic.create_oval(2, 2, 26, 26, fill="#1a2a3a", outline=ACCENT2, width=1.5)
        ic.create_text(14, 14, text="↻", fill=ACCENT2, font=("Segoe UI", 12, "bold"))

        tk.Label(row, text="Follow-up Message Preview",
                 font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side="left")

        count_badge = tk.Label(row,
                               text=f" {len(self.businesses)} eligible ",
                               font=("Segoe UI", 8, "bold"),
                               bg=ACCENT2, fg="#fff",
                               padx=6, pady=2)
        count_badge.pack(side="left", padx=10)

        tk.Label(hf, text="Send follow-up messages to businesses that have been messaged but haven't replied yet",
                 font=("Segoe UI", 8), bg=SURFACE, fg=MUTED).pack(anchor="w", padx=20)

    def _footer(self):
        bar = tk.Frame(self.win, bg=SURFACE, height=64)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x")

        btn_row = tk.Frame(bar, bg=SURFACE)
        btn_row.pack(fill="x", padx=20, pady=12)

        _HoverButton(btn_row, "✉  Send & Mark Follow-up",
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

    def _content(self):
        outer = tk.Frame(self.win, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        left  = tk.Frame(outer, bg=BG, width=220)
        right = tk.Frame(outer, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 12))
        right.pack(side="left", fill="both", expand=True)
        left.pack_propagate(False)

        self._options_panel(left)
        self._preview_panel(right)

    def _options_panel(self, parent):
        # ── Navigation card ──
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

        # ── Tone card ──
        tone_card = _Card(parent, accent_bar=True)
        tone_card.pack(fill="x", pady=(0, 8))

        tone_inner = tk.Frame(tone_card, bg=SURFACE)
        tone_inner.pack(fill="x", padx=10, pady=10)

        _SectionLabel(tone_inner, "Follow-up Tone").pack(anchor="w", pady=(0, 6))

        combo = _StyledCombo(tone_inner,
                             textvariable=self.tone_var,
                             values=["friendly", "professional", "urgent"],
                             width=20)
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", lambda _: self.update_review())

        # ── Follow-up interval card ──
        interval_card = _Card(parent, accent_bar=True)
        interval_card.pack(fill="x", pady=(0, 8))

        interval_inner = tk.Frame(interval_card, bg=SURFACE)
        interval_inner.pack(fill="x", padx=10, pady=10)

        _SectionLabel(interval_inner, "Follow-up Date").pack(anchor="w", pady=(0, 6))

        days_row = tk.Frame(interval_inner, bg=SURFACE)
        days_row.pack(fill="x")

        tk.Label(days_row, text="Days from now:",
                 bg=SURFACE, fg=TEXT2,
                 font=("Segoe UI", 9)).pack(side="left")

        days_spin = tk.Spinbox(days_row,
                               from_=1, to=30,
                               textvariable=self.followup_days,
                               width=4,
                               bg=SURFACE, fg=TEXT,
                               buttonbackground=SURFACE,
                               relief="flat",
                               font=("Segoe UI", 9))
        days_spin.pack(side="left", padx=(6, 0))
        days_spin.bind("<KeyRelease>", lambda _: self._update_date_label())
        days_spin.bind("<<Increment>>", lambda _: self._update_date_label())
        days_spin.bind("<<Decrement>>", lambda _: self._update_date_label())

        self.date_preview_label = tk.Label(interval_inner, text="",
                                           bg=SURFACE, fg=ACCENT,
                                           font=("Segoe UI", 8, "bold"))
        self.date_preview_label.pack(anchor="w", pady=(4, 0))
        self._update_date_label()

        # ── Sections card ──
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

    def _update_date_label(self):
        days = self.followup_days.get()
        future = datetime.now() + timedelta(days=days)
        self.date_preview_label.config(text=f"→ Will be set to: {future.strftime('%d-%m-%Y')}")

    def _preview_panel(self, parent):
        info_bar = tk.Frame(parent, bg=BG)
        info_bar.pack(fill="x", pady=(0, 8))

        tk.Label(info_bar, text="FOLLOW-UP MESSAGE",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(side="left")

        self.info_label = tk.Label(info_bar, text="",
                                   font=("Segoe UI", 8),
                                   bg=BG, fg=TEXT2)
        self.info_label.pack(side="right")

        preview_card = tk.Frame(parent, bg=SURFACE,
                                highlightbackground=BORDER,
                                highlightthickness=1)
        preview_card.pack(fill="both", expand=True)

        tk.Frame(preview_card, bg=ACCENT2, height=2).pack(fill="x")

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

        biz = self.businesses[idx]
        name = biz.get("Business Name", "")

        msg = generate_followup_message(
            tone=self.tone_var.get(),
            biz_name=name,
            sections=[s for s in SECTIONS if self.sections_vars[s].get()]
        )

        self.prev_text.delete("1.0", "end")
        self.prev_text.insert("1.0", msg)
        self.prev_text.see("1.0")

        biz_type = biz.get("Type", "Other") or "Other"
        phone = str(biz.get("Phone No", ""))
        date_sent = str(biz.get("Date", ""))
        self.info_label.config(
            text=f"{name}  ·  {biz_type}  ·  {phone}  ·  Added: {date_sent}")

        if len(self.businesses) > 1 and hasattr(self, "nav_label"):
            self.nav_label.config(
                text=f"Showing {idx + 1} of {len(self.businesses)}")

    def _mark_followup(self, biz):
        days = self.followup_days.get()
        followup_date = (datetime.now() + timedelta(days=days)).strftime("%d-%m-%Y")
        wb = self.controller.get_writable_wb()
        ws = wb.active
        from lib.utils.actions import mark_followup
        mark_followup(wb, ws, config.EXCEL_PATH, biz, followup_date)

    def send_current(self):
        idx = self.current_idx.get()
        if idx >= len(self.businesses):
            return

        biz = self.businesses[idx]
        name = str(biz.get("Business Name", ""))

        msg = generate_followup_message(
            tone=self.tone_var.get(),
            biz_name=name,
            sections=[s for s in SECTIONS if self.sections_vars[s].get()]
        )

        open_whatsapp_send(biz.get("Phone No", ""), name, msg)

        if messagebox.askyesno("Mark Follow-up Sent",
                               f"Did you send the follow-up to {name}?\n\n"
                               f"Follow-up date will be set to {self.followup_days.get()} days from now.",
                               parent=self.win):
            self._mark_followup(biz)
            # Remove from working list
            self.businesses.pop(idx)
            if self.businesses:
                self.current_idx.set(min(idx, len(self.businesses) - 1))
                self.update_review()
            else:
                messagebox.showinfo("All Done", "All follow-ups have been sent!", parent=self.win)
                self.win.destroy()
                return

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
        all_marked = True
        for biz in list(self.businesses):
            name = str(biz.get("Business Name", ""))

            msg = generate_followup_message(
                tone=self.tone_var.get(),
                biz_name=name,
                sections=[s for s in SECTIONS if self.sections_vars[s].get()]
            )

            open_whatsapp_send(biz.get("Phone No", ""), name, msg)
            sent_count += 1
            if sent_count < count:
                time.sleep(2)

        if messagebox.askyesno(
                "Mark Follow-ups Sent",
                f"Opened {sent_count} tabs.\n\n"
                "Mark all these businesses as 'Follow-up Sent' in Excel?\n"
                f"Follow-up date will be set to {self.followup_days.get()} days from now.",
                parent=self.win):
            for biz in self.businesses:
                self._mark_followup(biz)
        else:
            all_marked = False

        messagebox.showinfo("Done",
                            f"Opened WhatsApp for {sent_count} businesses",
                            parent=self.win)
        if all_marked:
            self.win.destroy()
