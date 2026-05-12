import tkinter as tk
from tkinter import ttk, messagebox
import threading
from lib import config
from lib.utils.scraper import scrape_google_maps
from lib.utils.excel_func import check_duplicate_in_excel, add_business_to_excel
from lib.utils.logger import log_info, log_error


# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0f0f13"
SURFACE   = "#1a1a24"
BORDER    = "#2a2a3a"
ACCENT    = "#4285F4"
ACCENT_HV = "#2a6fd6"
TEXT      = "#e8e8f0"
MUTED     = "#7a7a95"
SUCCESS   = "#34a853"
RADIUS    = 10          # used where Canvas fakes rounded rects


def _rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a filled rounded rectangle on a Canvas."""
    pts = [
        x1+r, y1,  x2-r, y1,
        x2,   y1,  x2,   y1+r,
        x2,   y2-r, x2,  y2,
        x2-r, y2,  x1+r, y2,
        x1,   y2,  x1,   y2-r,
        x1,   y1+r, x1,  y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class _HoverButton(tk.Label):
    """Flat label that behaves like a button with hover colour."""
    def __init__(self, parent, text, command, bg=ACCENT, fg=TEXT,
                 hover_bg=ACCENT_HV, font=("Segoe UI", 10, "bold"), **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         cursor="hand2", padx=18, pady=9, **kw)
        self._bg, self._hbg, self._cmd = bg, hover_bg, command
        self.bind("<Enter>",  lambda _: self.config(bg=self._hbg))
        self.bind("<Leave>",  lambda _: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda _: self._cmd())


class _StyledCombo(ttk.Combobox):
    """Combobox with a dark-friendly ttk style applied."""
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
                        selectforeground=TEXT,
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


class LeadFinderDialog:
    W, H = 400, 340

    def __init__(self, parent, controller):
        self.parent     = parent
        self.controller = controller
        self.no_web_var = tk.BooleanVar(value=False)

        self.win = tk.Toplevel(parent)
        self.win.title("Find New Leads")
        self.win.geometry(f"{self.W}x{self.H}")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.overrideredirect(False)   # keep OS chrome
        
        # centre on screen
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"{self.W}x{self.H}+"
                          f"{(sw-self.W)//2}+{(sh-self.H)//2}")
        
        self._build()


    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self._header()
        self._body()

    def _header(self):
        hf = tk.Frame(self.win, bg=SURFACE, height=72)
        hf.pack(fill="x")
        hf.pack_propagate(False)

        # coloured top stripe  (Google-brand bar)
        stripe = tk.Canvas(hf, height=3, bg=SURFACE, highlightthickness=0)
        stripe.pack(fill="x")
        stripe.update_idletasks()
        w = self.W
        seg = w // 4
        for i, col in enumerate(["#4285F4", "#34a853", "#fbbc05", "#ea4335"]):
            stripe.create_rectangle(i*seg, 0, (i+1)*seg, 3, fill=col, outline="")

        # title row
        row = tk.Frame(hf, bg=SURFACE)
        row.pack(fill="x", padx=20, pady=(8, 0))

        # map-pin icon (Canvas circle + dot)
        ic = tk.Canvas(row, width=26, height=26, bg=SURFACE,
                       highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        ic.create_oval(3, 3, 23, 23, fill="#1c3a6e", outline=ACCENT, width=1.5)
        ic.create_oval(10, 10, 16, 16, fill=ACCENT, outline="")

        tk.Label(row, text="Find New Leads", font=("Segoe UI", 13, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side="left")

        tk.Label(hf, text="Search Google Maps for businesses",
                 font=("Segoe UI", 9), bg=SURFACE, fg=MUTED).pack(
                 anchor="w", padx=20)

    def _field(self, parent, label, values):
        """Returns (frame, combobox)."""
        tk.Label(parent, text=label.upper(),
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(14, 3))

        combo = _StyledCombo(parent, values=values, width=34)
        combo.pack(fill="x")
        return combo

    def _body(self):
        body = tk.Frame(self.win, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=4)
        
        from lib.utils.paste_parser import get_locations
        self.type_combo = self._field(body, "Business type", config.BIZ_TYPES)
        self.loc_combo  = self._field(body, "Location",      get_locations())
        
        # No Website filter
        web_frame = tk.Frame(body, bg=BG)
        web_frame.pack(fill="x", pady=(14, 0))
        tk.Checkbutton(web_frame, text="Find only businesses without website", 
                       variable=self.no_web_var, bg=BG, fg=TEXT, 
                       selectcolor=BG, font=("Segoe UI", 9), 
                       activebackground=BG, activeforeground=TEXT).pack(anchor="w")
        
        # separator
        sep = tk.Frame(body, bg=BORDER, height=1)
        sep.pack(fill="x", pady=16)
        
        # button row
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x")
        
        cancel_btn = _HoverButton(btn_row, "Cancel",
                                   command=self.win.destroy,
                                   bg="#23232f", hover_bg="#2e2e3f",
                                   fg=MUTED, font=("Segoe UI", 10))
        cancel_btn.pack(side="left")
        
        scrape_btn = _HoverButton(btn_row, "⟳  Start Scraping",
                                   command=self._search,
                                   bg=ACCENT, hover_bg=ACCENT_HV,
                                   fg="#fff", font=("Segoe UI", 10, "bold"))
        scrape_btn.pack(side="right")
        
        # status bar
        status_row = tk.Frame(self.win, bg=BG)
        status_row.pack(fill="x", padx=22, pady=(0, 16))
        
        dot = tk.Canvas(status_row, width=8, height=8, bg=BG,
                        highlightthickness=0)
        dot.pack(side="left", padx=(0, 6))
        dot.create_oval(1, 1, 7, 7, fill=SUCCESS, outline="")
        
        tk.Label(status_row, text="Ready · duplicate check enabled",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(side="left")


    # ── Logic (unchanged) ────────────────────────────────────────────────────

    def _search(self):
        btype = self.type_combo.get().strip()
        loc   = self.loc_combo.get().strip()
        if not btype or not loc:
            messagebox.showwarning("Required", "Please select a business type and location.",
                                    parent=self.win)
            return
        
        no_web = self.no_web_var.get()
        
        def run():
            try:
                # Create a set of existing business names to avoid clicking duplicates
                existing_names = {str(b.get("Business Name", "")).lower() for b in self.controller.businesses if b.get("Business Name")}
                
                log_info(f"Starting auto-scrape for {btype} in {loc} (no_web={no_web})")

                existing_names = {str(b.get("Business Name", "")).lower()
                                  for b in self.controller.businesses if b.get("Business Name")}

                # Scraper now handles all filtering internally and scrolls until
                # it finds exactly 10 valid (mobile, non-duplicate) leads.
                results = scrape_google_maps(btype, loc, no_website_only=no_web,
                                             existing_leads=existing_names, target=10)

                if not results:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Finished", "No new leads found."))
                    return

                wb_write = self.controller.get_writable_wb()
                ws_write = wb_write.active

                count = 0
                for lead in results:
                    try:
                        add_business_to_excel(wb_write, ws_write, config.EXCEL_PATH, lead)
                        count += 1
                        print(f"Saved ({count}): {lead['Business Name']}")
                    except Exception as e:
                        log_error(f"Failed to save lead {lead.get('Business Name')}: {e}")
                
                self.parent.after(0, lambda: [
                    self.controller.refresh(),
                    messagebox.showinfo("Done",
                        f"Added {count} new lead{'s' if count != 1 else ''}!")
                ])
                log_info(f"Added {count} leads for {btype} in {loc}")
    
            except Exception as e:
                log_error(f"Critical scraper error: {e}", exc_info=True)
                self.parent.after(0, lambda: messagebox.showerror(
                    "Scraper Error",
                    "A critical error occurred.\nCheck app_logs.txt for details."))
        
        threading.Thread(target=run, daemon=True).start()
        self.win.destroy()