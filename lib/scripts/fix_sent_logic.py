#!/usr/bin/env python3
"""Fix WhatsApp sending and marking sent logic."""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Create a helper method _mark_businesses_sent to handle the Excel update without a prompt
# We will insert this before action_mark_sent
mark_sent_helper = '''
    def _mark_businesses_sent(self, businesses):
        """Internal helper to mark specific businesses as sent without prompting."""
        wb_write = self.get_writable_wb()
        ws_write = wb_write.active
        for biz in businesses:
            from utils.actions import mark_sent
            mark_sent(wb_write, ws_write, config.EXCEL_PATH, biz)
        self.refresh()
'''

# Find where to insert it (before action_mark_sent)
insert_pos = content.find('    def action_mark_sent(self):')
if insert_pos == -1:
    print("ERROR: Could not find action_mark_sent")
    exit(1)

# Update action_mark_sent to use the helper
content = content.replace(
    '''    def action_mark_sent(self):
        businesses = self.get_selected()
        if not businesses:
            return
        result = messagebox.askyesno("Confirm", f"Mark {len(businesses)} business(es) as Sent?")
        if result:
            wb_write = self.get_writable_wb()
            ws_write = wb_write.active
            for biz in businesses:
                mark_sent(wb_write, ws_write, config.EXCEL_PATH, biz)
            self.refresh()''',
    '''    def action_mark_sent(self):
        businesses = self.get_selected()
        if not businesses:
            return
        if messagebox.askyesno("Confirm", f"Mark {len(businesses)} business(es) as Sent?"):
            self._mark_businesses_sent(businesses)'''
)

# Now fix the dialog functions in action_whatsapp_dialog
# Fix send_current: open WA -> prompt -> mark sent
send_current_fixed = '''        def send_current():
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
            
            if messagebox.askyesno("Mark Sent", f"Did you send the message to {name}?"):
                self._mark_businesses_sent([biz])
            
            messagebox.showinfo("Done", f"Process completed for {name}")'''

# Fix send_all: open all WA -> prompt once -> mark all sent
send_all_fixed = '''        def send_all():
            count = len(businesses)
            if not messagebox.askyesno("Confirm", f"Open wa.me links for {count} businesses, one by one?\\\\n\\\\nEach will open in a new tab. You will need to click Send on each."):
                return
            
            sent_count = 0
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
                sent_count += 1
                
                if sent_count < count:
                    time.sleep(2)

            if messagebox.askyesno("Mark Sent", f"Opened {sent_count} tabs. Mark all these businesses as Sent?"):
                self._mark_businesses_sent(businesses)
                
            messagebox.showinfo("Done", f"Opened WhatsApp for {sent_count} businesses")'''

# Use regex to replace the functions accurately
content = re.sub(
    r'def send_current\(\):.*?def send_all\(\):', 
    f'def send_current():\n{send_current_fixed}\n\n    def send_all():', 
    content, 
    flags=re.DOTALL
)
# We need to replace send_all specifically because the regex above only goes up to the def
# Let's just use a simpler replacement for the specific blocks if possible, or a comprehensive one.

# Since regex on multi-line is tricky, let's use a temporary marker
content = content.replace('        def send_current():', '##SEND_CURRENT##')
content = content.replace('        def send_all():', '##SEND_ALL##')

# Now we need to find the end of those functions to replace them
# This is getting messy, let's use a precise line-based approach or a custom script.
'''
# I will rewrite the logic in a separate file and apply it.

