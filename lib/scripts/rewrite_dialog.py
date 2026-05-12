#!/usr/bin/env python3
"""Rewrite action_whatsapp_dialog with all fixes."""

import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('    def action_whatsapp_dialog(self):')
end = content.find('    def action_mark_sent(self):', start)

if start == -1 or end == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

print(f"Found function at {start} to {end}")

# The new function with all fixes
new_func = '''    def action_whatsapp_dialog(self):
        businesses = self.get_selected()
        if not businesses:
            return
        if len(businesses) > 10:
            if not messagebox.askyesno("Confirm", f"Send WhatsApp to {len(businesses)} businesses?\\\\nThis will open multiple wa.me tabs."):
                return

        from utils.message_templates import SECTIONS, generate_message

        win = tk.Toplevel(self.root)
        win.title("WhatsApp Message Preview")
        win.geometry("750x700")
        win.configure(bg=config.COLORS["bg"])
        win.resizable(True, True)

        ws = win.winfo_screenwidth()
        hs = win.winfo_screenheight()
        x = (ws/2) - (750/2)
        y = (hs/2) - (700/2)
        win.geometry(f"750x700+{int(x)}+{int(y)}")

        # Variables
        current_idx = tk.IntVar(value=0)
        tone_var = tk.StringVar(value="friendly")
        no_website_var = tk.BooleanVar(value=False)
        sections_vars = {s: tk.BooleanVar(value=True) for s in SECTIONS}

        # === FUNCTIONS DEFINED FIRST ===
        def update_review():
            idx = current_idx.get()
            if idx >= len(businesses):
                return
            biz = businesses[idx]
            biz_type = biz.get("Type", "Other") or "Other"
            name = biz.get("Business Name", "")
            website = biz.get("Website", "")
            phone = str(biz.get("Phone No", ""))

            is_no_website = no_website_var.get() or not str(website).strip()

            msg = generate_message(
                biz_type=biz_type,
                tone=tone_var.get(),
                biz_name=name,
                no_website=is_no_website,
                sections=[s for s in SECTIONS if sections_vars[s].get()]
            )

            prev_text.delete("1.0", "end")
            prev_text.insert("1.0", msg)
            prev_text.see("1.0")

            info_label.config(text=f"Business {idx+1}/{len(businesses)}: {name} | Type: {biz_type} | Phone: {phone}")

        def send_current():
            idx = current_idx.get()
            if idx >= len(businesses):
                return
            biz = businesses[idx]
            name = str(biz.get("Business Name", ""))
            website = biz.get("Website", "")
            is_no_website = no_website_var.get() or not str(website).strip()

            msg = generate_message(
                biz_type=biz.get("Type", "Other") or "Other",
                tone=tone_var.get(),
                biz_name=name,
                no_website=is_no_website,
                sections=[s for s in SECTIONS if sections_vars[s].get()]
            )

            from utils.actions import open_whatsapp_send
            open_whatsapp_send(biz.get("Phone No", ""), name, msg)
            # Mark only this business as sent
            wb_write = self.get_writable_wb()
            ws_write = wb_write.active
            mark_sent(wb_write, ws_write, config.EXCEL_PATH, biz)
            self.refresh()
            messagebox.showinfo("Sent", f"Opened WhatsApp for {name}")

        def send_all():
            count = len(businesses)
            if not messagebox.askyesno("Confirm", f"Open wa.me links for {count} businesses, one by one?\\\\n\\\\nEach will open in a new tab. You will need to click Send on each."):
                return
            
            sent = 0
            for biz in businesses:
                name = str(biz.get("Business Name", ""))
                website = biz.get("Website", "")
                is_no_website = no_website_var.get() or not str(website).strip()

                msg = generate_message(
                    biz_type=biz.get("Type", "Other") or "Other",
                    tone=tone_var.get(),
                    biz_name=name,
                    no_website=is_no_website,
                    sections=[s for s in SECTIONS if sections_vars[s].get()]
                )

                from utils.actions import open_whatsapp_send
                open_whatsapp_send(biz.get("Phone No", ""), name, msg)
                # Mark each business as sent
                wb_write = self.get_writable_wb()
                ws_write = wb_write.active
                mark_sent(wb_write, ws_write, config.EXCEL_PATH, biz)
                sent += 1
                
                if sent < count:
                    time.sleep(2)

            self.refresh()
            messagebox.showinfo("Done", f"Opened WhatsApp for {sent} businesses")

        # === WIDGETS ===
        # Header
        header_frame = tk.Frame(win, bg=config.COLORS["accent"], height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=f"WhatsApp Messages ({len(businesses)} selected)", 
               font=("Segoe UI", 14, "bold"), bg=config.COLORS["accent"], fg="#000").pack(pady=12)

        # Main container
        main_container = tk.Frame(win, bg=config.COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Top bar with navigation
        top_bar = tk.Frame(main_container, bg=config.COLORS["bg"])
        top_bar.pack(fill="x", pady=(0,10))

        # Navigation buttons (only show if multiple businesses)
        if len(businesses) > 1:
            nav_frame = tk.Frame(top_bar, bg=config.COLORS["bg"])
            nav_frame.pack(side="left")
            tk.Button(nav_frame, text="< Prev", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(max(0, current_idx.get()-1)), update_review()]).pack(side="left", padx=(0,5))
            tk.Button(nav_frame, text="Next >", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1)), update_review()]).pack(side="left", padx=5))

        # Info label
        info_label = tk.Label(top_bar, text="", bg=config.COLORS["bg"], 
                              fg=config.COLORS["muted"], font=("Segoe UI", 9))
        info_label.pack(side="right")

        # SCROLLABLE Preview box (Canvas + Scrollbar)
        preview_outer = tk.Frame(main_container, bg=config.COLORS["surface"], relief="solid", bd=1)
        preview_outer.pack(fill="both", expand=True, pady=(0,10))

        preview_canvas = tk.Canvas(preview_outer, bg=config.COLORS["surface"], highlightthickness=0)
        preview_scrollbar = tk.Scrollbar(preview_outer, orient="vertical", command=preview_canvas.yview)
        preview_scrollable = tk.Frame(preview_canvas, bg=config.COLORS["surface"])

        preview_scrollable.bind("<Configure>", lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all")))
        preview_canvas.create_window((0,0), window=preview_scrollable, anchor="nw")
        preview_canvas.configure(yscrollcommand=preview_scrollbar.set)

        preview_canvas.pack(side="left", fill="both", expand=True, padx=(15,0), pady=15)
        preview_scrollbar.pack(side="right", fill="y", pady=15, padx=(0,15))

        prev_text = tk.Text(preview_scrollable, font=("Segoe UI", 11), 
                         bg=config.COLORS["surface"], fg=config.COLORS["text"], 
                         wrap="word", relief="flat", height=18)
        prev_text.pack(fill="both", expand=True, padx=15, pady=15)

        # Options panel
        options_outer = tk.Frame(main_container, bg=config.COLORS["bg"])
        options_outer.pack(fill="x", pady=(0,10))

        # Tone selector
        tone_frame = tk.Frame(options_outer, bg=config.COLORS["surface2"], relief="solid", bd=1)
        tone_frame.pack(fill="x", pady=5, padx=5)
        tk.Label(tone_frame, text="Tone:", bg=config.COLORS["surface2"], 
                 fg=config.COLORS["muted"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(5,0))
        tone_combo = ttk.Combobox(tone_frame, textvariable=tone_var, 
                                    values=["friendly", "professional", "urgent"], 
                                    width=20, state="readonly")
        tone_combo.pack(anchor="w", padx=10, pady=5)
        tone_combo.bind("<<ComboboxSelected>>", lambda e: update_review())

        # No website checkbox
        check_frame = tk.Frame(options_outer, bg=config.COLORS["surface2"], relief="solid", bd=1)
        check_frame.pack(fill="x", pady=5, padx=5)
        tk.Checkbutton(check_frame, text="No website (use 'no website' problem text)", 
                      variable=no_website_var, bg=config.COLORS["surface2"], 
                      fg=config.COLORS["text"], selectcolor=config.COLORS["bg"],
                      font=("Segoe UI", 9), command=update_review).pack(anchor="w", padx=10, pady=5)

        # Sections checkboxes
        sections_frame = tk.Frame(options_outer, bg=config.COLORS["surface2"], relief="solid", bd=1)
        sections_frame.pack(fill="x", pady=5, padx=5)
        tk.Label(sections_frame, text="Include sections:", bg=config.COLORS["surface2"], 
                 fg=config.COLORS["muted"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(5,0))
        for s in SECTIONS:
            tk.Checkbutton(sections_frame, text=s.replace("_", " ").title(), 
                           variable=sections_vars[s], bg=config.COLORS["surface2"], 
                           fg=config.COLORS["text"], selectcolor=config.COLORS["bg"],
                           font=("Segoe UI", 9), command=update_review).pack(anchor="w", padx=15, pady=2)

        # Button bar
        btn_bar = tk.Frame(main_container, bg=config.COLORS["bg"])
        btn_bar.pack(fill="x", pady=10)

        tk.Button(btn_bar, text="Send This", bg=config.COLORS["accent"], fg="#000", 
                 font=("Segoe UI", 10, "bold"), padx=20, pady=8,
                 command=send_current).pack(side="left", padx=5)
        
        if len(businesses) > 1:
            tk.Button(btn_bar, text="Send All (one-by-one)", bg="#075E54", fg="#fff", 
                     font=("Segoe UI", 10, "bold"), padx=20, pady=8,
                     command=send_all).pack(side="left", padx=5)

        tk.Button(btn_bar, text="Close", bg=config.COLORS["surface2"], fg=config.COLORS["text"], 
                 font=("Segoe UI", 10), padx=20, pady=8,
                 command=win.destroy).pack(side="right", padx=5)

        update_review()
'''

# Replace
new_content = content[:start] + new_func + '\n\n' + content[end:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: All fixes applied!")
print("1. Preview now scrolls (Canvas + Scrollbar)")
print("2. Send All opens multiple tabs correctly")
print("3. Mark Sent works properly after sending")

