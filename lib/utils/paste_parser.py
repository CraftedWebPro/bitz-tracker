import re
import pyperclip
import os

_locations_cache = None

def get_locations():
    global _locations_cache
    if _locations_cache is not None:
        return _locations_cache
    
    _locations_cache = []
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "locations.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            _locations_cache = [line.strip() for line in f if line.strip()]
    return _locations_cache

def parse_google_maps_text(text):
    result = {"name": "", "phone": "", "website": "", "location": ""}
    
    if not text:
        return result
    
    locations = get_locations()
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    name_patterns = [
        r'^([A-Z][A-Za-z\s&]+(?:Pvt|Ltd|Inc|Corporation|Company)?)',
        r'^([A-Z][A-Za-z\s&\'-]+)',
    ]
    for line in lines[:5]:
        for pattern in name_patterns:
            match = re.match(pattern, line.strip())
            if match and len(match.group(1)) > 2:
                result["name"] = match.group(1).strip()
                break
        if result["name"]:
            break
    
    phone_patterns = [
        r'\+91[\s\-]?(\d{5})[\s\-]?(\d{5})',
        r'(\d{5})[\s\-]?(\d{5})',
        r'\+?91(\d{10})',
        r'\(?\d{3,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
    ]
    for line in lines:
        for pattern in phone_patterns:
            match = re.search(pattern, line)
            if match:
                phone = match.group(0)
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 10:
                    result["phone"] = digits[-10:]
                    break
        if result["phone"]:
            break
    
    url_pattern = r'(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?'
    for line in lines:
        if 'google.com' in line.lower() or 'maps.google' in line.lower():
            continue
        match = re.search(url_pattern, line)
        if match:
            url = match.group(0)
            if '.' in url and len(url) > 4:
                if not url.startswith('http'):
                    url = 'https://' + url
                result["website"] = url
                break
    
    locations = get_locations()
    all_text = ' '.join(lines).lower()
    
    for loc in locations:
        if loc.lower() in all_text:
            result["location"] = loc
            break
    else:
        address_patterns = [
            r'[A-Z][a-z]+,\s*[A-Z][a-z]+',
            r'[A-Z][a-z]+\s+Road',
            r'[A-Z][a-z]+\s+Market',
            r'Ward\s+No\.?\s*\d+',
            r'\d+,\s*[A-Z][a-z]+',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                result["location"] = match.group(0).strip()
                break
    
    return result

def get_clipboard_text():
    try:
        return pyperclip.paste()
    except:
        return ""

def extract_from_clipboard():
    text = get_clipboard_text()
    return parse_google_maps_text(text)
