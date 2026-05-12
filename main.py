# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
from lib import config
from lib.controllers.app_controller import AppController
from lib.ui.whatsapp_dialog import WhatsAppDialog
from lib.ui.followup_dialog import FollowUpDialog
from lib.ui.lead_finder import LeadFinderDialog
from lib.ui.add_business_dialog import AddBusinessDialog
from lib.ui.notes_dialog import NotesDialog
from lib.ui.profile_dialog import ProfileDialog
from lib.utils.excel_func import (load_excel, save_excel, get_all_businesses,
                                   add_business_to_excel, update_row_in_excel,
                                   check_duplicate_in_excel)
from lib.utils.actions import (search_google, mark_sent,
                                 mark_replied, mark_followup, mark_not_interested,
                                 add_note, generate_wa_link, open_whatsapp_send)
from lib.utils.paste_parser import extract_from_clipboard, get_locations

# ── Palette — Slate Pro ───────────────────────────────────────────────────────
BG       = "#0d1117"   # GitHub-dark base
SURFACE  = "#161b22"   # Slightly lighter surface
CARD     = "#1c2128"   # Card / header bg — slightly lighter for better contrast
BORDER   = "#30363d"   # Subtle border
BORDER2  = "#4d8ef0"   # Active border — brighter
ACCENT   = "#4d94ff"   # Bright blue — more vivid
ACCENT_D = "#2f81f7"   # Darker accent for hover
GREEN    = "#56d364"   # Success green — brighter
GREEN_D  = "#3fb950"   # Hover green
RED      = "#ff6b6b"   # Danger red — softer
RED_D    = "#f85149"
GOLD     = "#f0c040"   # Warning gold — more vivid
GOLD_D   = "#d4a017"
PURPLE   = "#d2a8ff"   # Purple — brighter
TEXT     = "#e6edf3"   # Primary text
TEXT2    = "#b1bac4"   # Secondary / muted — much brighter (was #8b949e)
TEXT3    = "#768390"   # Disabled / muted — much brighter (was #484f58)
WHITE    = "#ffffff"
FONT     = "Segoe UI"
MONO     = "Consolas"


def _styles():
    s = ttk.Style()
    s.theme_use("clam")

    # Combobox
    s.configure("A.TCombobox",
                fieldbackground=CARD, background=CARD,
                foreground=TEXT, selectbackground=BORDER2,
                selectforeground=WHITE, bordercolor=BORDER,
                arrowcolor=TEXT2, relief="flat", padding=(8, 5))
    s.map("A.TCombobox",
          fieldbackground=[("readonly", CARD)],
          foreground=[("readonly", TEXT)],
          bordercolor=[("focus", ACCENT)],
          arrowcolor=[("active", ACCENT)])

    # Treeview
    s.configure("A.Treeview",
                background=SURFACE,
                foreground=TEXT,
                fieldbackground=SURFACE,
                rowheight=30, borderwidth=0,
                font=(FONT, 9))
    s.configure("A.Treeview.Heading",
                background=CARD, foreground=TEXT2,
                font=(FONT, 8, "bold"), relief="flat",
                borderwidth=0, padding=(6, 8))
    s.map("A.Treeview",
          background=[("selected", "#1c3a5e")],
          foreground=[("selected", WHITE)])
    s.map("A.Treeview.Heading",
          background=[("active", BORDER)],
          foreground=[("active", WHITE)])

    # Scrollbars — ultra thin
    for o in ("Vertical", "Horizontal"):
        s.configure(f"A.{o}.TScrollbar",
                    background=BORDER, troughcolor=SURFACE,
                    bordercolor=SURFACE, arrowcolor=TEXT3,
                    relief="flat", width=6)


# ── Button widget ─────────────────────────────────────────────────────────────

class Btn(tk.Label):
    """Flat hover button."""
    def __init__(self, parent, text, cmd,
                 bg=CARD, fg=TEXT2, hbg=BORDER, hfg=WHITE,
                 font_size=9, bold=False, px=12, py=6, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=(FONT, font_size, "bold" if bold else "normal"),
                         cursor="hand2", padx=px, pady=py, **kw)
        self._bg, self._fg, self._hbg, self._hfg = bg, fg, hbg, hfg
        self.bind("<Enter>",    lambda _: self.config(bg=self._hbg, fg=self._hfg))
        self.bind("<Leave>",    lambda _: self.config(bg=self._bg,  fg=self._fg))
        self.bind("<Button-1>", lambda _: cmd())


class PillBtn(tk.Label):
    """Accent-coloured pill button for primary actions."""
    def __init__(self, parent, text, cmd,
                 bg=ACCENT, fg=WHITE, hbg=ACCENT_D,
                 font_size=9, bold=True, px=16, py=7, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg,
                         font=(FONT, font_size, "bold" if bold else "normal"),
                         cursor="hand2", padx=px, pady=py, **kw)
        self.bind("<Enter>",    lambda _: self.config(bg=hbg))
        self.bind("<Leave>",    lambda _: self.config(bg=bg))
        self.bind("<Button-1>", lambda _: cmd())


# ── App ───────────────────────────────────────────────────────────────────────

class BizTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BizTracker — Vivek Tamang")
        self.root.state("zoomed")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        _styles()
        self.controller = AppController(self)
        self.setup_ui()
        self.setup_global_hotkey()

    # ── Data ──────────────────────────────────────────────────────────────────

    def refresh(self):
        self.controller.refresh()

    def update_filters(self):
        locs  = sorted({str(b.get("Location","")) for b in self.controller.businesses if b.get("Location")})
        locs  = sorted(set(locs + sorted(get_locations())))
        types = sorted({str(b.get("Type","")) for b in self.controller.businesses if b.get("Type")})
        if hasattr(self, "loc_combo"):  self.loc_combo["values"]  = ["all"] + locs
        if hasattr(self, "type_combo"): self.type_combo["values"] = ["all"] + types

    def populate_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.controller.get_filtered_businesses(
            self.search_var.get(), self.status_var.get(), self.type_var.get(),
            self.loc_var.get(), self.date_var.get(), self.sent_var.get(),
            self.reply_var.get(), self.follow_var.get()
        )
        for i, b in enumerate(rows):
            converted = str(b.get("Converted?","")).strip().lower() == "yes"
            tag = "conv" if converted else ("a" if i % 2 else "b")
            self.tree.insert("", "end", tags=(tag,), values=(
                b.get("SL No",""),      b.get("Date",""),
                b.get("Business Name",""), b.get("Website",""),
                b.get("Problem",""),    b.get("Type",""),
                b.get("Location",""),   b.get("Phone No",""),
                b.get("Msg Sent?",""),  b.get("Reply Came?",""),
                b.get("Follow Up Sent?",""), b.get("Follow Up Date",""),
                b.get("Converted?",""),
                (b.get("Notes") or "")[:35],
            ))
        if hasattr(self, "_count"):
            self._count.config(text=f"{len(rows)} records")
        self._refresh_stats()

    # ── UI ────────────────────────────────────────────────────────────────────

    def setup_ui(self):
        self._header()
        self._stats_bar()
        self._search_filter()
        self._table()
        self._actions()
        self._statusbar()
        self.controller.start_followup_scheduler()
        self.update_status()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ── Header ────────────────────────────────────────────────────────────────

    def _header(self):
        h = tk.Frame(self.root, bg=CARD, height=52)
        h.pack(fill="x")
        h.pack_propagate(False)

        # ── Left: wordmark ──
        left = tk.Frame(h, bg=CARD)
        left.pack(side="left", padx=20, fill="y")

        # Small square logo mark
        logo = tk.Canvas(left, width=28, height=28, bg=CARD, highlightthickness=0)
        logo.pack(side="left", pady=12)
        logo.create_rectangle(0, 0, 28, 28, fill=ACCENT, outline="")
        logo.create_text(14, 14, text="BT", fill=WHITE, font=(FONT, 9, "bold"))

        tk.Label(left, text=" BizTracker",
                 font=(FONT, 13, "bold"), bg=CARD, fg=WHITE).pack(side="left")
        tk.Label(left, text="  /  Vivek Tamang",
                 font=(FONT, 9), bg=CARD, fg=TEXT2).pack(side="left")

        # Thin accent bottom border on header
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    # ── Stats bar ─────────────────────────────────────────────────────────────

    def _stats_bar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=76)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self._slbls = {}
        items = [
            ("Total",      "total",     TEXT,   "All businesses"),
            ("Sent",       "sent",      ACCENT, "Messages sent"),
            ("Replied",    "replied",   GREEN,  "Replies received"),
            ("Follow-ups", "followups", GOLD,   "Scheduled follow-ups"),
            ("Converted",  "converted", PURPLE, "Deals closed"),
            ("Pending",    "pending",   TEXT2,  "Awaiting response"),
        ]

        inner = tk.Frame(bar, bg=SURFACE)
        inner.pack(side="left", padx=20, fill="y")

        for i, (label, key, color, _tip) in enumerate(items):
            if i:
                tk.Frame(inner, bg=BORDER, width=1).pack(
                    side="left", fill="y", padx=18, pady=14)
            cell = tk.Frame(inner, bg=SURFACE)
            cell.pack(side="left", pady=10)

            lbl = tk.Label(cell, text="0", bg=SURFACE, fg=color,
                           font=(FONT, 22, "bold"))
            lbl.pack(anchor="w")
            tk.Label(cell, text=label, bg=SURFACE, fg=TEXT2,
                     font=(FONT, 8, "bold")).pack(anchor="w")
            self._slbls[key] = lbl

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    def _refresh_stats(self):
        b = self.controller.businesses
        sent = sum(1 for x in b if str(x.get("Msg Sent?","")).strip().lower()=="yes")
        d = {
            "total":     len(b),
            "sent":      sent,
            "replied":   sum(1 for x in b if str(x.get("Reply Came?","")).strip().lower()=="yes"),
            "followups": sum(1 for x in b if str(x.get("Follow Up Sent?","")).strip().lower()=="yes"),
            "converted": sum(1 for x in b if str(x.get("Converted?","")).strip().lower()=="yes"),
            "pending":   len(b) - sent,
        }
        for k, v in d.items():
            if k in self._slbls:
                self._slbls[k].config(text=str(v))

    # ── Search + filters ──────────────────────────────────────────────────────

    def _search_filter(self):
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="x", padx=16, pady=(10, 6))

        # ── Row 1: search box ──
        r1 = tk.Frame(wrap, bg=BG)
        r1.pack(fill="x", pady=(0, 8))

        # Search pill
        sbox = tk.Frame(r1, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        sbox.pack(side="left")

        tk.Label(sbox, text="  Search", bg=CARD, fg=TEXT3,
                 font=(FONT, 9)).pack(side="left")

        self.search_var = tk.StringVar()
        ent = tk.Entry(sbox, textvariable=self.search_var,
                       bg=CARD, fg=TEXT, insertbackground=ACCENT,
                       relief="flat", font=(FONT, 10), bd=0, width=32)
        ent.pack(side="left", ipady=7, padx=(4, 10))
        ent.bind("<KeyRelease>", lambda e: self.populate_tree())
        ent.bind("<FocusIn>",  lambda e: sbox.config(highlightbackground=ACCENT))
        ent.bind("<FocusOut>", lambda e: sbox.config(highlightbackground=BORDER))

        self._count = tk.Label(r1, text="", bg=BG, fg=TEXT2,
                               font=(MONO, 8))
        self._count.pack(side="left", padx=12)

        # ── Row 2: filter dropdowns + Apply Filters + Refresh/Stats/Add Business ──
        r2 = tk.Frame(wrap, bg=BG)
        r2.pack(fill="x", pady=(0, 4))

        filters = [
            ("Status",     "status_var",  config.STATUS_OPTIONS,                   12),
            ("Type",       "type_var",    ["all"] + config.BIZ_TYPES,              10),
            ("Location",   "loc_var",     ["all"],                                 12),
            ("Date",       "date_var",    ["all","Today","This Week","This Month"], 10),
            ("Sent?",      "sent_var",    config.YES_NO_OPTIONS,                    5),
            ("Reply?",     "reply_var",   config.YES_NO_OPTIONS,                    5),
            ("Follow-up?", "follow_var",  config.YES_NO_OPTIONS,                    6),
        ]
        for label, attr, vals, w in filters:
            col = tk.Frame(r2, bg=BG)
            col.pack(side="left", padx=(0, 10))
            tk.Label(col, text=label.upper(), bg=BG, fg=TEXT2,
                     font=(FONT, 7, "bold")).pack(anchor="w", pady=(0, 2))
            var = tk.StringVar(value="all")
            setattr(self, attr, var)
            cb = ttk.Combobox(col, textvariable=var, values=vals,
                              width=w, style="A.TCombobox", state="readonly")
            cb.pack()
            if attr == "loc_var":  self.loc_combo  = cb
            if attr == "type_var": self.type_combo = cb

        # Apply Filters — right after dropdowns
        apply_col = tk.Frame(r2, bg=BG)
        apply_col.pack(side="left", padx=(8, 0))
        tk.Label(apply_col, text=" ", bg=BG).pack(pady=(0, 2))  # spacer for alignment
        PillBtn(apply_col, "Apply Filters", self.populate_tree,
                bg=ACCENT, hbg=ACCENT_D, fg=WHITE,
                font_size=9, px=12, py=5).pack()

        # ── Right side: Refresh / Stats / Add Business ──
        right_btns = tk.Frame(r2, bg=BG)
        right_btns.pack(side="right")

        PillBtn(right_btns, "+ Add Business", self.add_business,
                bg=GREEN, hbg=GREEN_D, fg=WHITE,
                px=12, py=5).pack(side="right", padx=(4, 0))

        Btn(right_btns, "Stats", self.show_stats,
            bg=CARD, fg=TEXT2, hbg=BORDER, hfg=WHITE,
            px=10, py=5).pack(side="right", padx=2)

        Btn(right_btns, "Refresh", self.refresh,
            bg=CARD, fg=TEXT2, hbg=BORDER, hfg=WHITE,
            px=10, py=5).pack(side="right", padx=2)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    # ── Table ─────────────────────────────────────────────────────────────────

    def _table(self):
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        cols = ("SL", "Date", "Business Name", "Website", "Problem",
                "Type", "Location", "Phone", "Sent", "Reply",
                "Follow-up", "Follow-up Date", "Converted", "Notes")
        widths = {
            "SL":36, "Date":82, "Business Name":155, "Website":180,
            "Problem":180, "Type":80, "Location":90, "Phone":105,
            "Sent":50, "Reply":50, "Follow-up":65,
            "Follow-up Date":108, "Converted":68, "Notes":200,
        }
        aligns = {
            "SL":"center", "Date":"center", "Business Name":"w", "Website":"w",
            "Problem":"w", "Type":"center", "Location":"center", "Phone":"center",
            "Sent":"center", "Reply":"center", "Follow-up":"center",
            "Follow-up Date":"center", "Converted":"center", "Notes":"w"
        }

        self.tree = ttk.Treeview(wrap, columns=cols, show="headings",
                                  selectmode="extended", style="A.Treeview")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths.get(col, 90),
                             anchor=aligns.get(col, "center"),
                             stretch=(col in ("Business Name","Website","Problem","Notes")))

        # Row alternating colours
        self.tree.tag_configure("a",    background=SURFACE,   foreground=TEXT)
        self.tree.tag_configure("b",    background=BG,        foreground=TEXT)
        self.tree.tag_configure("conv", background="#0d2a1a", foreground=GREEN)

        vsb = ttk.Scrollbar(wrap, orient="vertical",   command=self.tree.yview, style="A.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview, style="A.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

    # ── Action dock ───────────────────────────────────────────────────────────

    def _actions(self):
        dock = tk.Frame(self.root, bg=CARD)
        dock.pack(fill="x", side="bottom")
        tk.Frame(dock, bg=BORDER, height=1).pack(fill="x")  # top divider

        row = tk.Frame(dock, bg=CARD)
        row.pack(side="left", padx=10, pady=8, fill="y")

        def sep():
            tk.Frame(row, bg=BORDER, width=1).pack(
                side="left", fill="y", pady=3, padx=8)

        def b(text, cmd, fg=TEXT2, hfg=WHITE, bg=CARD, hbg=BORDER2):
            Btn(row, text, cmd, bg=bg, fg=fg, hbg=hbg, hfg=hfg,
                font_size=9, px=10, py=5).pack(side="left", padx=1)

        # Group 1 — Lead gen
        b("Find Leads",      self.find_leads,             fg=GOLD,   hfg=WHITE, hbg="#3d2800")
        sep()

        # Group 2 — Outreach
        b("Google",          self.action_google,          fg=TEXT2)
        b("WhatsApp",        self.action_whatsapp_dialog, fg=GREEN,  hfg=WHITE, hbg="#0e2f14")
        b("Follow-up Msg",   self.action_followup_dialog, fg="#4dc9f6", hfg=WHITE, hbg="#0d2a4a")
        sep()

        # Group 3 — Status
        b("Mark Sent",       self.action_mark_sent,       fg=ACCENT, hfg=WHITE, hbg="#0d2a4a")
        b("Follow Up",       self.action_followup,        fg=GOLD,   hfg=WHITE, hbg="#3d2800")
        b("Replied",         self.action_replied,         fg=TEXT2)
        sep()

        # Group 4 — Outcome
        b("Converted",       self.action_converted,       fg=GREEN,  hfg=WHITE, hbg="#0e2f14")
        b("Not Interested",  self.action_not_interested,  fg=RED,    hfg=WHITE, hbg="#3a0f0d")
        sep()

        # Group 5 — Misc
        b("Notes",           self.action_add_notes,       fg=PURPLE, hfg=WHITE, hbg="#261040")
        b("Settings",        self.action_settings,        fg=TEXT2)
        b("Logs",            self.view_logs,              fg=TEXT3)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _statusbar(self):
        sb = tk.Frame(self.root, bg=BG, height=24)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x")
        self.status_label = tk.Label(sb, text="", bg=BG, fg=TEXT2,
                                     font=(MONO, 8))
        self.status_label.pack(side="left", padx=16, pady=3)
        tk.Label(sb, text="BizTracker v2", bg=BG, fg=TEXT3,
                 font=(FONT, 8)).pack(side="right", padx=16)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def on_closing(self):
        self.controller.stop_scheduler()
        self.root.destroy()

    def update_status(self):
        self.status_label.config(text=self.controller.update_status_counts())
        self._refresh_stats()

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Please select one or more businesses first.")
            return []
        filtered = self.controller.get_filtered_businesses(
            self.search_var.get(), self.status_var.get(), self.type_var.get(),
            self.loc_var.get(), self.date_var.get(), self.sent_var.get(),
            self.reply_var.get(), self.follow_var.get()
        )
        return [filtered[self.tree.index(s)] for s in sel]

    def action_google(self):
        for biz in self.get_selected():
            from lib.utils.actions import search_google_maps
            search_google_maps(biz=biz)

    def action_whatsapp_dialog(self):
        businesses = self.get_selected()
        if not businesses: return
        if len(businesses) > 10:
            if not messagebox.askyesno("Confirm",
                    f"Open WhatsApp for {len(businesses)} businesses?"): return
        WhatsAppDialog(self.root, self.controller, businesses)

    def action_followup_dialog(self):
        businesses = self.get_selected()
        if not businesses: return
        FollowUpDialog(self.root, self.controller, businesses)
        self.refresh()

    def action_mark_sent(self):
        businesses = self.get_selected()
        if not businesses: return
        if messagebox.askyesno("Confirm", f"Mark {len(businesses)} as Sent?"):
            self.controller.mark_businesses_sent(businesses)
            self.refresh()

    def action_followup(self):
        businesses = self.get_selected()
        if not businesses: return
        default = (datetime.now() + timedelta(days=3)).strftime("%d-%m-%Y")
        date = simpledialog.askstring("Follow-up Date",
                                      "Enter follow-up date (dd-mm-YYYY):",
                                      initialvalue=default)
        if not date: return
        try: datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Invalid", "Use format dd-mm-YYYY"); return
        if messagebox.askyesno("Confirm", f"Set follow-up to {date} for {len(businesses)} business(es)?"):
            wb = self.controller.get_writable_wb(); ws = wb.active
            for biz in businesses: mark_followup(wb, ws, config.EXCEL_PATH, biz, date)
            self.refresh()

    def action_replied(self):
        businesses = self.get_selected()
        if not businesses: return
        if messagebox.askyesno("Confirm", f"Mark {len(businesses)} as Replied?"):
            wb = self.controller.get_writable_wb(); ws = wb.active
            for biz in businesses: mark_replied(wb, ws, config.EXCEL_PATH, biz)
            self.refresh()

    def action_not_interested(self):
        businesses = self.get_selected()
        if not businesses: return
        if messagebox.askyesno("Confirm", f"Mark {len(businesses)} as Not Interested?"):
            wb = self.controller.get_writable_wb(); ws = wb.active
            for biz in businesses: mark_not_interested(wb, ws, config.EXCEL_PATH, biz)
            self.refresh()

    def action_converted(self):
        businesses = self.get_selected()
        if not businesses: return
        if messagebox.askyesno("Confirm", f"Mark {len(businesses)} as Converted?"):
            wb = self.controller.get_writable_wb(); ws = wb.active
            for biz in businesses:
                from lib.utils.actions import mark_converted
                mark_converted(wb, ws, config.EXCEL_PATH, biz)
            self.refresh()

    def action_add_notes(self):
        businesses = self.get_selected()
        if not businesses: return
        NotesDialog(self.root, self.controller, businesses)

    def find_leads(self):   LeadFinderDialog(self.root, self.controller)
    def add_business(self): AddBusinessDialog(self.root, self.controller)
    def action_settings(self): ProfileDialog(self.root)

    def on_double_click(self, event):
        item = self.tree.identify("item", event.x, event.y)
        if item: self.tree.selection_set(item)

    def show_stats(self):
        b = self.controller.businesses
        sent     = sum(1 for x in b if str(x.get("Msg Sent?","")).strip().lower()=="yes")
        replied  = sum(1 for x in b if str(x.get("Reply Came?","")).strip().lower()=="yes")
        followup = sum(1 for x in b if str(x.get("Follow Up Sent?","")).strip().lower()=="yes")
        conv     = sum(1 for x in b if str(x.get("Converted?","")).strip().lower()=="yes")
        rate     = f"{replied/sent*100:.1f}%" if sent else "—"
        messagebox.showinfo("Stats",
            f"{'Total':<20} {len(b)}\n"
            f"{'Sent':<20} {sent}\n"
            f"{'Replied':<20} {replied}\n"
            f"{'Reply Rate':<20} {rate}\n"
            f"{'Follow-ups':<20} {followup}\n"
            f"{'Converted':<20} {conv}")

    def view_logs(self):
        import os
        log_path = os.path.join(config.BASE_DIR, "app_logs.txt")
        if os.path.exists(log_path): os.startfile(log_path)
        else: messagebox.showinfo("Logs", "No logs found yet.")

    def setup_global_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey("ctrl+shift+a", self.quick_add_from_clipboard)
        except Exception: pass

    def quick_add_from_clipboard(self):
        parsed = extract_from_clipboard()
        if not parsed["name"] and not parsed["phone"]:
            self.root.after(0, lambda: messagebox.showwarning(
                "No Data", "Copy business info first, then press Ctrl+Shift+A"))
            return
        self.root.after(0, lambda: self.show_quick_add_dialog(parsed))

    def show_quick_add_dialog(self, parsed):
        dialog = AddBusinessDialog(self.root, self.controller)
        for field, key in [("Business Name","name"),("Phone No","phone"),("Website","website")]:
            if parsed.get(key):
                dialog.entries[field].delete(0, "end")
                dialog.entries[field].insert(0, parsed[key])
        if parsed.get("location"):
            dialog.loc_combo.set(parsed["location"])


if __name__ == "__main__":
    root = tk.Tk()
    app = BizTrackerApp(root)
    root.mainloop()