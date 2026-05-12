import os
from datetime import datetime, timedelta
from tkinter import messagebox
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from lib import config
from lib.utils.excel_func import load_excel, get_all_businesses, update_row_in_excel

def _parse_date(date_str):
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


class AppController:
    def __init__(self, app):
        self.app = app
        self.wb = None
        self.ws = None
        self.businesses = []
        self.scheduler = None
        self.load_excel()

    def load_excel(self):
        try:
            self.wb = load_excel(config.EXCEL_PATH, data_only=True)
            self.ws = self.wb.active
            self.businesses = get_all_businesses(self.ws)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open Excel: {e}")

    def refresh(self):
        self.load_excel()
        if hasattr(self.app, 'update_filters'):
            self.app.update_filters()
        if hasattr(self.app, 'populate_tree'):
            self.app.populate_tree()

    def get_writable_wb(self):
        return load_excel(config.EXCEL_PATH, data_only=False)

    def get_filtered_businesses(self, search="", status="all", btype="all", loc_filter="all", 
                                 date_filter="all", sent_filter="all", reply_filter="all", follow_filter="all"):
        search = str(search).lower()
        
        filtered = []
        for biz in self.businesses:
            name = str(biz.get("Business Name", "")).lower()
            phone = str(biz.get("Phone No", "")).lower()
            loc = str(biz.get("Location", "")).lower()
            
            if search and search not in name and search not in phone and search not in loc:
                continue

            if btype != "all" and biz.get("Type", "") != btype:
                continue

            if loc_filter != "all" and biz.get("Location", "") != loc_filter:
                continue

            msg_sent = str(biz.get("Msg Sent?", "")).strip().lower()
            reply = str(biz.get("Reply Came?", "")).strip().lower()
            follow = str(biz.get("Follow Up Sent?", "")).strip().lower()

            if sent_filter == "Yes" and msg_sent not in ["yes", "y"]:
                continue
            if sent_filter == "No" and msg_sent in ["yes", "y"]:
                continue
            
            if reply_filter == "Yes" and reply not in ["yes", "y"]:
                continue
            if reply_filter == "No" and reply in ["yes", "y"]:
                continue
            
            if follow_filter == "Yes" and follow not in ["yes", "y"]:
                continue
            if follow_filter == "No" and follow in ["yes", "y"]:
                continue

            if status == "Not Contacted" and msg_sent:
                continue
            if status == "Messaged" and msg_sent not in ["yes", "y"]:
                continue
            if status == "Replied" and reply not in ["yes", "y"]:
                continue
            if status == "Follow-up Due":
                if msg_sent not in ["yes", "y"] or reply in ["yes", "y"]:
                    continue
                if follow in ["yes", "y"]:
                    follow_date_str = str(biz.get("Follow Up Date", "")).strip()
                    if follow_date_str:
                        try:
                            fd = datetime.strptime(follow_date_str, "%d-%m-%Y")
                            if fd > datetime.now():
                                continue
                        except:
                            pass
                else:
                    date_str = str(biz.get("Date", "")).strip()
                    if date_str:
                        try:
                            biz_date = datetime.strptime(date_str, "%d-%m-%Y")
                            min_date = datetime.now() - timedelta(days=config.FOLLOWUP_INTERVAL_DAYS)
                            if biz_date > min_date:
                                continue
                        except:
                            pass
                    else:
                        continue

            if status == "Follow-up Sent" and follow not in ["yes", "y"]:
                continue

            if date_filter != "all":
                date_str = biz.get("Date", "")
                try:
                    biz_date = _parse_date(date_str)
                    today = datetime.now()
                    if date_filter == "Today" and biz_date.date() != today.date():
                        continue
                    elif date_filter == "This Week":
                        week_ago = today - timedelta(days=7)
                        if biz_date < week_ago:
                            continue
                    elif date_filter == "This Month":
                        if biz_date.month != today.month or biz_date.year != today.year:
                            continue
                except:
                    pass

            filtered.append(biz)
        return filtered

    def update_status_counts(self):
        total = len(self.businesses)
        sent = sum(1 for b in self.businesses if str(b.get("Msg Sent?", "")).strip().lower() == "yes")
        replied = sum(1 for b in self.businesses if str(b.get("Reply Came?", "")).strip().lower() == "yes")
        today = datetime.now().strftime("%d-%m-%Y")
        due = sum(1 for b in self.businesses
                 if str(b.get("Follow Up Sent?", "")).strip().lower() == "yes"
                 and str(b.get("Follow Up Date", "")).strip()
                 and str(b.get("Follow Up Date", "")).strip() <= today)
        return f"Total: {total} | Sent: {sent} | Replied: {replied} | Due Follow-ups: {due}"

    def mark_businesses_sent(self, businesses):
        wb_write = self.get_writable_wb()
        ws_write = wb_write.active
        for biz in businesses:
            update_row_in_excel(wb_write, ws_write, config.EXCEL_PATH, biz, **{"Msg Sent?": "yes"})
        # Notes logic is handled separately in actions.py or we can add it here
        # But to stay consistent with your current main.py, we keep the core status update.

    def start_followup_scheduler(self):
        def check_due():
            today = datetime.now().strftime("%d-%m-%Y")
            due = [b for b in self.businesses
                   if str(b.get("Follow Up Sent?", "")).strip().lower() == "yes"
                   and str(b.get("Follow Up Date", "")).strip()
                   and str(b.get("Follow Up Date", "")).strip() <= today]
            if due:
                names = ", ".join(str(b.get("Business Name", "")) for b in due[:3])
                if len(due) > 3:
                    names += f" and {len(due)-3} more"
                self.app.root.after(0, lambda: messagebox.showinfo("Follow-ups Due!", f"{len(due)} follow-up(s) due today:\n\n{names}"))
        
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(func=check_due, trigger=IntervalTrigger(hours=1))
        self.scheduler.start()

    def stop_scheduler(self):
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
