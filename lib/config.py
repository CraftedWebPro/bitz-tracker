import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXCEL_PATH = os.path.join(BASE_DIR, "DAILY_CHECK_LIST.xlsx")
EXCEL_PATH_OLD = os.path.join(BASE_DIR, "DAILY_CHECK_LIST_OLD.xlsx")

COLORS = {
    "bg": "#0B0E14",       # Very dark blue-grey
    "surface": "#151921",   # Dark grey-blue
    "card": "#1C222D",      # Lighter grey-blue
    "border": "#2D3545",    # Subtle border
    "accent": "#5C7CFA",    # Indigo accent
    "accent2": "#FF6B6B",   # Soft red
    "gold": "#FFD43B",      # Soft gold
    "purple": "#BE4BDB",    # Soft purple
    "text": "#D1D5DB",      # Light grey text
    "text2": "#9CA3AF",     # Muted text
    "text3": "#6B7280",     # Darker muted text
    "white": "#FFFFFF",
    "green": "#51CF66",     # Soft green
    "red": "#FF6B6B",       # Soft red
}

BIZ_TYPES = ["Tourism", "Hotel", "School", "Restaurant", "Shop", "Gym", "Clinic", "Other"]

STATUS_OPTIONS = ["all", "Not Contacted", "Messaged", "Replied", "Follow-up Due", "Follow-up Sent"]

YES_NO_OPTIONS = ["all", "Yes", "No"]

FOLLOWUP_INTERVAL_DAYS = 2  # Min days after initial contact before follow-up is due
