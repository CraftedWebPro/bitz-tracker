# BizTracker

> A desktop lead management tool — scrape Google Maps leads, send WhatsApp outreach, track follow-ups, all from one dark-themed Tkinter UI.
>
> **Built for Indian market** — phone number validation, WhatsApp links, and location data are India-specific.

---

## Features

### Lead Scraping
- **Google Maps Auto-Scraper** — Enter a business type and location, Playwright opens Chrome and scrapes business names, phone numbers, and websites
- **Duplicate detection** — Skips already-captured names and phone numbers across sessions
- **Smart location fallback** — Automatically tries nearby areas when results run out (e.g., Gangtok → East Sikkim → Sikkim)
- **Clipboard import** — Copy text from anywhere and press `Ctrl+Shift+A` to auto-fill the Add Business form

### WhatsApp Outreach
- **Message preview dialog** — Compose messages in 3 tones (friendly / professional / urgent)
- **Section toggles** — Include/exclude greeting, problem statement, social proof, CTA, and signature
- **Send one-by-one or bulk** — Opens wa.me links in browser tabs
- **Auto-mark sent** — Option to mark businesses as messaged after sending
- **Profile system** — Your name, profession, location, and website are editable from **Settings** (no code editing needed)

### Follow-up Management
- **Follow-up message dialog** — Dedicated modal for sending follow-up messages (separate templates)
- **Eligibility filtering** — Only shows businesses that are messaged, not replied, and no follow-up sent yet
- **Auto date scheduling** — Follow-up date is set automatically (default: 2 days from now)
- **Chained follow-ups** — After a follow-up is sent and its date arrives, it shows up again for another round
- **Desktop notifications** — `plyer`-based system tray alerts for due follow-ups

### Status Tracking
- Grid filters: **Not Contacted** / **Messaged** / **Replied** / **Follow-up Due** / **Follow-up Sent**
- Column filters: Sent?, Reply?, Follow-up? (Yes / No / All)
- Date range filters: Today / This Week / This Month
- One-click status buttons: Mark Sent, Replied, Follow Up, Converted, Not Interested
- Stats bar with live counts (Total, Sent, Replied, Follow-ups, Converted, Pending)
- Notes dialog for each business

---

## Prerequisites

- **Python 3.10+**
- **Windows** (primary target; Linux/macOS may need adjustments for `keyboard` and notification libraries)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/biz-tracker.git
cd biz-tracker

# 2. Run the setup script (installs deps, Playwright, and launches app)
python setup.py
```

Or just double-click `setup.py` from File Explorer.

---

## Quick Start

### 1. First run — set your profile
Click **Settings** in the action dock (bottom bar) and fill in:

| Field | Example |
|---|---|
| Your Name | `Vivek Tamang` |
| Profession | `web developer` |
| Profession Title | `Web Developer` |
| Location | `Siliguri` |
| Website | `https://www.craftedwebpro.com` |

These are used in every WhatsApp message — intros and signatures will use your details automatically.

### 2. Find leads
Click **Find Leads**, pick a business type and location, set a target count. Playwright opens Chrome and scrapes Google Maps.

### 3. Add businesses manually
Click **+ Add Business** to enter data by hand. Or copy text from anywhere and press `Ctrl+Shift+A` to auto-fill.

### 4. Send outreach messages
Select rows → **WhatsApp** → preview, adjust tone/sections, and send. Mark as sent when done.

### 5. Track & follow up
Use **Mark Sent**, **Replied**, **Follow Up** buttons to update each row. When enough days pass, filter by **Follow-up Due** and use **Follow-up Msg** to send reminders.

### 6. Close the deal
Mark as **Converted** when a lead becomes a client.

---

## Project Structure

```
biz-tracker/
├── main.py                          # App entry point
├── setup.py                         # One-click install + launch
├── run.bat                          # Quick launcher
├── requirements.txt                 # Python dependencies
├── DAILY_CHECK_LIST.xlsx            # Excel data store
├── DISCLAIMER.md
├── LICENSE
├── data/
│   ├── locations.txt                # Known locations for auto-detection
│   └── profile.json                 # Your name, website, etc.
├── lib/
│   ├── config.py                    # App-wide constants & palette
│   ├── controllers/
│   │   └── app_controller.py        # Business logic, filters, scheduler
│   ├── ui/
│   │   ├── whatsapp_dialog.py       # Initial outreach message dialog
│   │   ├── followup_dialog.py       # Follow-up message dialog
│   │   ├── lead_finder.py           # Google Maps scraper dialog
│   │   ├── add_business_dialog.py   # Manual entry form
│   │   ├── profile_dialog.py        # Profile/settings editor
│   │   ├── notes_dialog.py          # Notes editor
│   │   └── __init__.py
│   └── utils/
│       ├── scraper.py               # Playwright-based Maps scraper
│       ├── message_templates.py      # Outreach message templates
│       ├── followup_templates.py     # Follow-up message templates
│       ├── profile.py               # Profile load/save/apply
│       ├── actions.py               # Status update helpers
│       ├── excel_func.py            # Excel read/write layer
│       ├── paste_parser.py          # Clipboard text parser
│       ├── followup_checker.py      # Due follow-up notification script
│       └── logger.py                # Logging utility
└── app_logs.txt                     # Runtime logs
```

---

## Configuration

### Profile (from the UI)
Click **Settings** in the app — edit name, profession, location, website. Saved to `data/profile.json`.

### App settings (`lib/config.py`)

| Setting | Default | Description |
|---|---|---|
| `FOLLOWUP_INTERVAL_DAYS` | `2` | Min days after initial contact before follow-up is due |
| `BIZ_TYPES` | `Tourism, Hotel, School...` | Business categories used in filters & scraper |
| `STATUS_OPTIONS` | `all, Not Contacted...` | Available status filters |

---

## Tech Stack

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

## Contact

For file structure questions, edits, or custom modifications:

**Vivek Tamang** — craftedwebpro@gmail.com

---

## License

MIT
