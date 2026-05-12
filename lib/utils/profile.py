import json
import os

_path = None
_cache = None

DEFAULT = {
    "name": "Your Name",
    "profession": "web developer",
    "profession_title": "Web Developer",
    "location": "Your City",
    "website": "https://example.com",
}


def _get_path():
    global _path
    if _path is None:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        _path = os.path.join(base, "data", "profile.json")
    return _path


def load():
    global _cache
    if _cache is not None:
        return _cache
    p = _get_path()
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                _cache = {**DEFAULT, **data}
                return _cache
        except Exception:
            pass
    _cache = dict(DEFAULT)
    return _cache


def save(data):
    global _cache
    merged = {**DEFAULT, **data}
    _cache = merged
    p = _get_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
    except Exception as e:
        raise IOError(f"Could not save profile: {e}")


def apply(text):
    p = load()
    return text.replace("{NAME}", p["name"]) \
                .replace("{PROFESSION}", p["profession"]) \
                .replace("{PROFESSION_TITLE}", p["profession_title"]) \
                .replace("{LOCATION}", p["location"]) \
                .replace("{WEBSITE}", p["website"])
