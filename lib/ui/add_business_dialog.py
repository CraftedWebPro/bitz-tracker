import tkinter as tk
from tkinter import ttk, messagebox
from lib import config
from lib.utils.excel_func import load_excel, add_business_to_excel, check_duplicate_in_excel
from lib.utils.paste_parser import extract_from_clipboard, get_locations

class AddBusinessDialog:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        
        self.win = tk.Toplevel(parent)
        self.win.title("Add Business")
        self.win.geometry("450x480")
        self.win.configure(bg=config.COLORS["surface"])
        self.win.resizable(False, False)
        
        # Center window
        ws = self.win.winfo_screenwidth()
        hs = self.win.winfo_screenheight()
        x = (ws/2) - (450/2)
        y = (hs/2) - (480/2)
        self.win.geometry(f"450x480+{int(x)}+{int(y)}")
        
        self.setup_ui()

    def setup_ui(self):
        header_frame = tk.Frame(self.win, bg=config.COLORS["accent"], height=50)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="Add New Business", font=("Segoe UI", 14, "bold"), bg=config.COLORS["accent"], fg="#000").pack(pady=12)
        
        content_frame = tk.Frame(self.win, bg=config.COLORS["surface"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        fields = ["Business Name", "Phone No", "Website", "Problem"]
        self.entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(content_frame, text=field, bg=config.COLORS["surface"], fg=config.COLORS["text2"], font=("Segoe UI", 10)).grid(row=i, column=0, padx=5, pady=8, sticky="w")
            entry = tk.Entry(content_frame, width=32, font=("Segoe UI", 10))
            entry.grid(row=i, column=1, padx=5, pady=8)
            self.entries[field] = entry
        
        tk.Label(content_frame, text="Location", bg=config.COLORS["surface"], fg=config.COLORS["text2"], font=("Segoe UI", 10)).grid(row=len(fields), column=0, padx=5, pady=8, sticky="w")
        self.loc_combo = ttk.Combobox(content_frame, values=get_locations(), width=30, font=("Segoe UI", 10))
        self.loc_combo.grid(row=len(fields), column=1, padx=5, pady=8)
        self.entries["Location"] = self.loc_combo
        
        tk.Label(content_frame, text="Type", bg=config.COLORS["surface"], fg=config.COLORS["text2"], font=("Segoe UI", 10)).grid(row=len(fields)+1, column=0, padx=5, pady=8, sticky="w")
        self.type_combo = ttk.Combobox(content_frame, values=config.BIZ_TYPES, width=30, font=("Segoe UI", 10))
        self.type_combo.grid(row=len(fields)+1, column=1, padx=5, pady=8)
        self.entries["Type"] = self.type_combo
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        self.status_label = tk.Label(content_frame, text="", bg=config.COLORS["surface"], fg=config.COLORS["accent"], font=("Segoe UI", 9))
        self.status_label.grid(row=len(fields)+2, column=0, columnspan=2, pady=5)
        
        btn_frame = tk.Frame(content_frame, bg=config.COLORS["surface"])
        btn_frame.grid(row=len(fields)+3, column=0, columnspan=2, pady=10, sticky="ew")
        
        tk.Button(btn_frame, text=" Paste from Clipboard ", bg="#FFC107", fg="#000", font=("Segoe UI", 9), command=self.paste_from_clipboard).pack(side="left", padx=10)
        tk.Button(btn_frame, text=" Save Business ", bg=config.COLORS["accent"], fg="#000", font=("Segoe UI", 10, "bold"), command=self.save).pack(side="left", padx=10)

    def paste_from_clipboard(self):
        parsed = extract_from_clipboard()
        if parsed["name"]:
            self.entries["Business Name"].delete(0, "end")
            self.entries["Business Name"].insert(0, parsed["name"])
        if parsed["phone"]:
            self.entries["Phone No"].delete(0, "end")
            self.entries["Phone No"].insert(0, parsed["phone"])
        if parsed["website"]:
            self.entries["Website"].delete(0, "end")
            self.entries["Website"].insert(0, parsed["website"])
        if parsed["location"]:
            self.loc_combo.set(parsed["location"])
        
        msg = f"Pasted:\nName: {parsed['name']}\nPhone: {parsed['phone']}\nWebsite: {parsed['website']}\nLocation: {parsed['location']}"
        if not parsed["name"] and not parsed["phone"]:
            msg = "Could not parse. Please enter manually."
        self.status_label.config(text=msg[:50], fg=config.COLORS["accent"] if parsed["name"] else config.COLORS["danger"])

    def save(self):
        name = self.entries["Business Name"].get().strip()
        phone = self.entries["Phone No"].get().strip()
        
        if not name or not phone:
            messagebox.showwarning("Required", "Name and Phone are required")
            return
        
        found = check_duplicate_in_excel(self.controller.businesses, name, phone)
        if found:
            result = messagebox.askyesno("Duplicate Found", f"Already exists!\n\nName: {found.get('Business Name')}\nPhone: {found.get('Phone No')}\n\nAdd anyway?")
            if not result: return
        
        data = {
            "Business Name": self.entries["Business Name"].get(),
            "Phone No": self.entries["Phone No"].get(),
            "Website": self.entries["Website"].get(),
            "Location": self.entries["Location"].get(),
            "Problem": self.entries["Problem"].get(),
            "Type": self.entries["Type"].get(),
            "Notes": ""
        }
        
        wb_write = self.controller.get_writable_wb()
        add_business_to_excel(wb_write, wb_write.active, config.EXCEL_PATH, data)
        self.win.destroy()
        self.controller.refresh()
