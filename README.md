<div align="center">

# 🗂️ BizTracker

**A desktop lead machine for the Indian market.**
Scrape Google Maps · Send WhatsApp outreach · Track follow-ups · Close deals — all from one dark-themed Tkinter UI.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-informational?style=flat-square&logo=windows&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Made for India](https://img.shields.io/badge/Made%20for-🇮🇳%20India-orange?style=flat-square)](https://github.com)

</div>

---

## ✨ Features

### 🔍 Lead Scraping
- **Google Maps Auto-Scraper** — Enter a business type and location; Playwright opens Chrome and collects names, phone numbers, and websites automatically
- **Duplicate detection** — Skips names and numbers already in your sheet, across sessions
- **Smart location fallback** — When results run dry, automatically tries nearby areas *(e.g. Gangtok → East Sikkim → Sikkim)*
- **Clipboard import** — Copy any text, press `Ctrl+Shift+A`, and the Add Business form fills itself

### 💬 WhatsApp Outreach
- **Message preview dialog** — Compose in 3 tones: *Friendly*, *Professional*, or *Urgent*
- **Section toggles** — Individually include/exclude greeting, problem statement, social proof, CTA, and signature
- **One-by-one or bulk send** — Opens `wa.me` links directly in your browser
- **Auto-mark sent** — Optionally mark businesses as messaged right after sending
- **Profile system** — Your name, profession, location, and website are set once in **Settings** and flow into every message automatically

### 🔁 Follow-up Management
- **Follow-up message dialog** — Separate modal with dedicated templates for follow-ups
- **Eligibility filtering** — Only shows businesses that are messaged, not replied, and haven't had a follow-up yet
- **Auto date scheduling** — Follow-up date is set automatically *(default: 2 days from initial contact)*
- **Chained follow-ups** — After a follow-up date passes, the lead surfaces again for the next round
- **Desktop notifications** — `plyer`-based system tray alerts when follow-ups are due

### 📊 Status Tracking
| What | How |
|---|---|
| Grid filters | Not Contacted · Messaged · Replied · Follow-up Due · Follow-up Sent |
| Column filters | Sent? · Reply? · Follow-up? — Yes / No / All |
| Date range filters | Today · This Week · This Month |
| Action buttons | Mark Sent · Replied · Follow Up · Converted · Not Interested |
| Stats bar | Live counts: Total · Sent · Replied · Follow-ups · Converted · Pending |
| Notes | Per-business notes dialog |

---

## 🛠️ Prerequisites

- **Python 3.10+**
- **Windows** *(primary target — `keyboard` and notification libraries may need adjustments on Linux/macOS)*

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/biz-tracker.git
cd biz-tracker

# 2. Run the setup script — installs deps, Playwright, and launches the app
python setup.py
```

> Or just **double-click `setup.py`** from File Explorer — no terminal needed.

---

## ⚡ Quick Start

### 1 · Set your profile
Click **Settings** in the action dock (bottom bar) and fill in your details:

| Field | Example |
|---|---|
| Your Name | `Vivek Tamang` |
| Profession | `web developer` |
| Profession Title | `Web Developer` |
| Location | `Siliguri` |
| Website | `https://www.craftedwebpro.com` |

These flow into every WhatsApp message — intros and signatures use your details automatically.

### 2 · Find leads
Click **Find Leads** → pick a business type and location → set a target count. Playwright opens Chrome and scrapes Google Maps.

### 3 · Add businesses manually
Click **+ Add Business** to enter data by hand, or copy text from anywhere and press `Ctrl+Shift+A` to auto-fill the form.

### 4 · Send outreach
Select rows → **WhatsApp** → preview, adjust tone and sections → send. Mark as sent when done.

### 5 · Track & follow up
Use **Mark Sent**, **Replied**, and **Follow Up** to update each row. Filter by **Follow-up Due** when reminders are needed, then use **Follow-up Msg** to send them.

### 6 · Close the deal
Mark as **Converted** when a lead becomes a client. 🎉

---

## 📁 Project Structure

```
biz-tracker/
├── main.py                        # App entry point
├── setup.py                       # One-click install + launch
├── run.bat                        # Quick launcher
├── requirements.txt               # Python dependencies
├── DAILY_CHECK_LIST.xlsx          # Excel data store
├── DISCLAIMER.md
├── LICENSE
│
├── data/
│   ├── locations.txt              # Known locations for auto-detection
│   └── profile.json               # Your name, website, etc.
│
└── lib/
    ├── config.py                  # App-wide constants & colour palette
    ├── controllers/
    │   └── app_controller.py      # Business logic, filters, scheduler
    ├── ui/
    │   ├── whatsapp_dialog.py     # Initial outreach message dialog
    │   ├── followup_dialog.py     # Follow-up message dialog
    │   ├── lead_finder.py         # Google Maps scraper dialog
    │   ├── add_business_dialog.py # Manual entry form
    │   ├── profile_dialog.py      # Profile / settings editor
    │   ├── notes_dialog.py        # Notes editor
    │   └── __init__.py
    └── utils/
        ├── scraper.py             # Playwright-based Maps scraper
        ├── message_templates.py   # Outreach message templates
        ├── followup_templates.py  # Follow-up message templates
        ├── profile.py             # Profile load / save / apply
        ├── actions.py             # Status update helpers
        ├── excel_func.py          # Excel read/write layer
        ├── paste_parser.py        # Clipboard text parser
        ├── followup_checker.py    # Due follow-up notification script
        └── logger.py              # Logging utility
```

---

## ⚙️ Configuration

### Profile — from the UI
Click **Settings** → edit name, profession, location, website. Saved to `data/profile.json`.

### App settings — `lib/config.py`

| Setting | Default | Description |
|---|---|---|
| `FOLLOWUP_INTERVAL_DAYS` | `2` | Minimum days after initial contact before a follow-up is due |
| `BIZ_TYPES` | `Tourism, Hotel, School…` | Business categories used in filters and the scraper |
| `STATUS_OPTIONS` | `all, Not Contacted…` | Available status filter values |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| UI | Python Tkinter (ttk, themed) |
| Scraping | Playwright (Chromium) |
| Data | OpenPyXL (Excel `.xlsx`) |
| Scheduling | APScheduler (background follow-up checks) |
| Notifications | Plyer (desktop alerts) |
| Hotkeys | Keyboard (global `Ctrl+Shift+A`) |
| Clipboard | Pyperclip |

---

## 📬 Contact

**Vivek Tamang** — [craftedwebpro@gmail.com](mailto:craftedwebpro@gmail.com)

---

## 📄 License

[MIT](LICENSE) © Vivek Tamang