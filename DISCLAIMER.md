# Disclaimer

This software uses **Playwright** (headful Chromium automation) to interact with **Google Maps** in a way that simulates human browsing for legitimate business lead generation purposes.

## Responsible Use

By using this software, you acknowledge that:

1. **Rate limiting & terms** — Automated scraping of Google Maps may violate Google's Terms of Service. This tool is designed for **personal, limited-scale use** (e.g., finding local businesses to offer web development services). Do not use it for mass data harvesting, reselling data, or any activity that could disrupt Google's services.

2. **No warranty** — The author provides no guarantee that this tool complies with Google's current ToS. Use at your own risk. Google may block your IP, rate-limit your account, or take other action if you send excessive requests.

3. **Educational purpose** — This project is shared for **educational and portfolio purposes**. It demonstrates how Playwright can be used for browser automation in a desktop Tkinter application.

4. **No liability** — The author is not responsible for any damages, account bans, or legal issues arising from misuse of this software. You are solely responsible for how you use it.

## WhatsApp & Outreach

The WhatsApp integration simply opens `wa.me` links in your browser — it does **not** send messages via the WhatsApp Business API or automate sending in any way. Each message requires manual confirmation (clicking Send in the browser).

## Profile & Personal Identity

The app includes a **profile system** (`data/profile.json`) that inserts your name, profession, and website into WhatsApp messages.

- The default profile contains **placeholder values** (`"Your Name"`, `"Your City"`, etc.). You **must** update it via **Settings → Save** before sending messages.
- The original author's name appears nowhere in the default templates or profile.
- If you fork or redistribute this project, ensure you remove or replace any personal information that may have been left as examples.
- The author is **not responsible** for messages sent by others using this software, including cases where the sender failed to update their profile.

## Data Privacy

All business data is stored locally in an Excel file on your machine. No data is transmitted to any third party or remote server by this software.
