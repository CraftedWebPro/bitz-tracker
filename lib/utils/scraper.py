import time
from playwright.sync_api import sync_playwright
from datetime import datetime


def _is_mobile(phone):
    if not phone:
        return False
    digits = "".join(filter(str.isdigit, phone))
    if not digits:
        return False
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) > 10:
        digits = digits[1:]
    return digits.startswith(('6', '7', '8', '9'))


def _get_fallback_locations(location):
    """
    Returns a list of nearby/broader locations to try when the primary location
    runs out of results. Add more entries here as needed.
    """
    location_l = location.lower().strip()
    fallbacks = {
        "gangtok":   ["East Sikkim", "Sikkim", "Rangpo", "Namchi", "Gyalshing"],
        "namchi":    ["South Sikkim", "Sikkim", "Jorethang", "Gangtok"],
        "gyalshing": ["West Sikkim", "Sikkim", "Namchi", "Gangtok"],
        "mangan":    ["North Sikkim", "Sikkim", "Gangtok"],
        "rangpo":    ["East Sikkim", "Sikkim", "Gangtok"],
        "jorethang": ["South Sikkim", "Sikkim", "Namchi"],
        "sikkim":    ["Darjeeling", "Kalimpong", "Siliguri"],
        "darjeeling":["Kalimpong", "Siliguri", "West Bengal"],
        "kalimpong": ["Darjeeling", "Siliguri", "Sikkim"],
        "siliguri":  ["Jalpaiguri", "Darjeeling", "North Bengal"],
    }
    for key, locs in fallbacks.items():
        if key in location_l:
            return locs
    # Generic fallback: try district → state
    return []


def _scrape_single_location(page, category, location, feed_js,
                             seen_names, seen_phones, session_clicked, processed_idx,
                             has_website_only, no_website_only, target, leads):
    """
    Scrape one location page. Mutates leads, seen_names, seen_phones,
    session_clicked, processed_idx in place.
    Returns True if we hit a real end-of-results, False if we hit target.
    """
    search_query = f"{category} in {location}"
    print(f"\n📍 Searching: {search_query}  ({len(leads)}/{target} so far)")

    page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")
    try:
        page.wait_for_selector('.hfpxzc', timeout=10000)
    except Exception as e:
        print(f"  No results for {location}: {e}")
        return True  # treat as exhausted

    # Reset per-location DOM tracking (new page = new indices)
    processed_idx.clear()
    scroll_attempts      = 0
    no_growth_streak     = 0   # consecutive scrolls with no new DOM entries
    MAX_SCROLLS          = 60
    NO_GROWTH_LIMIT      = 3   # stop only after 3 consecutive no-growth scrolls

    while len(leads) < target and scroll_attempts < MAX_SCROLLS:

        listings = page.query_selector_all('.hfpxzc')

        newly_processed = 0
        for idx, listing in enumerate(listings):
            if len(leads) >= target:
                break
            if idx in processed_idx:
                continue

            aria = listing.get_attribute('aria-label') or ""
            name_pre = aria.split(',')[0].strip()

            processed_idx.add(idx)
            newly_processed += 1

            if not name_pre or name_pre.lower() in session_clicked:
                continue
            if name_pre.lower() in seen_names:
                print(f"  Skip (already in DB): {name_pre}")
                session_clicked.add(name_pre.lower())
                continue

            session_clicked.add(name_pre.lower())

            try:
                listing.click()
                try:
                    page.wait_for_selector('.DUwDvf', timeout=3000)
                except:
                    continue

                name_el = page.query_selector('.DUwDvf')
                name    = name_el.inner_text().strip() if name_el else name_pre

                website_el = page.query_selector('a[aria-label*="Website"]')
                website    = website_el.get_attribute('href') if website_el else ""

                if has_website_only and not website:
                    continue
                if no_website_only and website:
                    continue

                phone_el = page.query_selector('button[aria-label*="Phone"]')
                phone    = (phone_el.get_attribute('aria-label')
                                    .replace("Phone: ", "").strip()
                            if phone_el else "")

                if not _is_mobile(phone):
                    print(f"  Skip (landline/no number): {name} ({phone})")
                    continue
                if phone and phone in seen_phones:
                    print(f"  Skip (duplicate phone): {name}")
                    continue
                if name.lower() in seen_names:
                    print(f"  Skip (duplicate name): {name}")
                    continue

                lead = {
                    "Business Name": name,
                    "Website":       website,
                    "Phone No":      phone,
                    "Location":      location,
                    "Type":          category,
                    "Problem":       "Leads Auto-Scraped",
                    "Notes":         f"Imported via Auto-Scraper on "
                                     f"{datetime.now().strftime('%d-%m-%Y')}"
                }
                leads.append(lead)
                seen_names.add(name.lower())
                seen_phones.add(phone)
                print(f"  ✓ Captured ({len(leads)}/{target}): {name}  [{location}]")

            except Exception:
                continue

        if len(leads) >= target:
            return False  # hit target — not exhausted, just done

        # ── Scroll ───────────────────────────────────────────────────────────
        prev_count = len(page.query_selector_all('.hfpxzc'))
        page.evaluate(f'{feed_js}.scrollBy(0, 3000)')
        time.sleep(2)
        scroll_attempts += 1
        new_count = len(page.query_selector_all('.hfpxzc'))

        # Real end-of-results message from Google Maps
        end_msg = page.query_selector("p.fontBodyMedium > span")
        if end_msg and "end of results" in (end_msg.inner_text() or "").lower():
            print(f"  ↳ Google Maps: end of results for {location}.")
            return True

        # Track consecutive no-growth scrolls
        if new_count <= prev_count:
            no_growth_streak += 1
        else:
            no_growth_streak = 0  # reset — new entries appeared

        print(f"  [Scroll {scroll_attempts}] {new_count} listings | "
              f"{len(leads)}/{target} valid | no-growth streak: {no_growth_streak}/{NO_GROWTH_LIMIT}")

        if no_growth_streak >= NO_GROWTH_LIMIT:
            print(f"  ↳ No new listings after {NO_GROWTH_LIMIT} scrolls — {location} exhausted.")
            return True

    return scroll_attempts >= MAX_SCROLLS  # True if hit ceiling


def scrape_google_maps(category, location, has_website_only=False, no_website_only=False,
                       existing_leads=None, target=10):
    """
    Scrapes Google Maps for `target` valid (mobile, non-duplicate) leads.
    Scrolls as long as needed. When a location runs out of results,
    automatically falls back to nearby locations until target is met.
    """
    leads        = []
    seen_names   = set(existing_leads) if existing_leads else set()
    seen_phones  = set()
    session_clicked = set()
    processed_idx   = set()

    feed_js = 'document.querySelector(\'div[role="feed"]\')'

    locations_to_try = [location] + _get_fallback_locations(location)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for loc in locations_to_try:
            if len(leads) >= target:
                break
            exhausted = _scrape_single_location(
                page, category, loc, feed_js,
                seen_names, seen_phones, session_clicked, processed_idx,
                has_website_only, no_website_only, target, leads
            )
            if not exhausted:
                break  # hit target mid-location
            remaining = target - len(leads)
            if remaining > 0:
                print(f"\n  ⚡ {loc} exhausted. Need {remaining} more — trying next location...")

        browser.close()

    print(f"\nDone: {len(leads)}/{target} valid leads collected.")
    return leads