# -*- coding: utf-8 -*-
import webbrowser
import urllib.parse
import os

def generate_wa_link(phone, message):
    phone = "".join(c for c in phone if c.isdigit() or c == "+")
    if not phone.startswith("+"):
        phone = "+91" + phone.lstrip("0")
    encoded = urllib.parse.quote(message, safe='', encoding='utf-8')
    return f"https://wa.me/{phone.lstrip('+')}?text={encoded}"

def open_whatsapp_send(phone, name, message):
    link = generate_wa_link(phone, message)
    webbrowser.open(link)
    return True, None

def search_google(biz=None, search_type=None, search_location=None):
    if biz:
        name = biz.get("Business Name", "")
        loc = biz.get("Location", "")
        query = f"{name} {loc}"
    elif search_type and search_location:
        query = f"{search_type} business {search_location}"
    else:
        query = "business"
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")

def search_google_maps(biz=None, search_type=None, search_location=None):
    if biz:
        name = biz.get("Business Name", "")
        loc = biz.get("Location", "")
        query = f"{name} {loc}"
    elif search_type and search_location:
        query = f"{search_type} {search_location}"
    else:
        query = "business"
    webbrowser.open(f"https://www.google.com/maps/search/{urllib.parse.quote(query)}")

def mark_sent(wb, ws, path, biz):
    from lib.utils.excel_func import update_row_in_excel
    from datetime import datetime
    existing_notes = str(biz.get("Notes", "") or "")
    new_note = f"{existing_notes}\nSent: {datetime.now().strftime('%d-%m-%Y')}".strip()
    update_row_in_excel(wb, ws, path, biz, **{"Msg Sent?": "yes", "Notes": new_note})

def mark_replied(wb, ws, path, biz):
    from lib.utils.excel_func import update_row_in_excel
    from datetime import datetime
    existing_notes = str(biz.get("Notes", "") or "")
    new_note = f"{existing_notes}\nReplied: {datetime.now().strftime('%d-%m-%Y')}".strip()
    update_row_in_excel(wb, ws, path, biz, **{"Reply Came?": "yes", "Notes": new_note})

def mark_followup(wb, ws, path, biz, followup_date=None):
    from lib.utils.excel_func import update_row_in_excel
    from datetime import datetime
    existing_notes = str(biz.get("Notes", "") or "")
    new_note = f"{existing_notes}\nFollow-up: {datetime.now().strftime('%d-%m-%Y')}".strip()
    date_str = followup_date if followup_date else ""
    update_row_in_excel(wb, ws, path, biz, **{"Follow Up Sent?": "yes", "Follow Up Date": date_str, "Notes": new_note})

def mark_not_interested(wb, ws, path, biz):
    from lib.utils.excel_func import update_row_in_excel
    from datetime import datetime
    existing_notes = str(biz.get("Notes", "") or "")
    new_note = f"{existing_notes}\nNot Interested: {datetime.now().strftime('%d-%m-%Y')}".strip()
    update_row_in_excel(wb, ws, path, biz, **{"Converted?": "No", "Notes": new_note})

def mark_converted(wb, ws, path, biz):
    from lib.utils.excel_func import update_row_in_excel
    from datetime import datetime
    existing_notes = str(biz.get("Notes", "") or "")
    new_note = f"{existing_notes}\nConverted: {datetime.now().strftime('%d-%m-%Y')}".strip()
    update_row_in_excel(wb, ws, path, biz, **{"Converted?": "Yes", "Notes": new_note})

def add_note(wb, ws, path, biz, note):
    from lib.utils.excel_func import update_row_in_excel
    update_row_in_excel(wb, ws, path, biz, **{"Notes": note})
