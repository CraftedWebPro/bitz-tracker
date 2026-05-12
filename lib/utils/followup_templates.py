# -*- coding: utf-8 -*-
FOLLOWUP_TEMPLATES = {
    "friendly": {
        "greeting": "Hey! Following up on my previous message about {BIZ}.",
        "body": "Just wanted to check if you had a chance to think about improving your online presence. A simple website can make a big difference for your business.",
        "cta": "Would you like to see some examples? Happy to share!",
        "signature": "- {NAME}\n{WEBSITE}"
    },
    "professional": {
        "greeting": "Hello,\nI'm following up on my earlier message regarding {BIZ}.",
        "body": "I wanted to revisit the conversation about building a website for your business. Many local businesses have seen great results with a proper online presence.",
        "cta": "I would be glad to share some relevant examples at your convenience.",
        "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}"
    },
    "urgent": {
        "greeting": "Hi! Quick follow-up about {BIZ}.",
        "body": "You may still be losing potential customers every day without a proper website. Competitors who have an online presence are getting the enquiries you should be getting.",
        "cta": "Let me send you a free review of how your business currently shows up online. No obligation.",
        "signature": "- {NAME}\n{WEBSITE}"
    }
}

SECTIONS = ["greeting", "body", "cta", "signature"]

def generate_followup_message(tone, biz_name, sections=None):
    if sections is None:
        sections = ["greeting", "body", "cta", "signature"]
    t = FOLLOWUP_TEMPLATES.get(tone, FOLLOWUP_TEMPLATES["friendly"])
    biz_str = f"*{biz_name}*" if biz_name else "your business"

    from lib.utils.profile import apply as apply_profile

    parts = []
    if "greeting" in sections:
        parts.append(t["greeting"].replace("{BIZ}", biz_str))
    if "body" in sections:
        parts.append(t["body"])
    if "cta" in sections:
        parts.append(t["cta"])
    if "signature" in sections:
        parts.append(apply_profile(t["signature"]))

    return "\n\n".join(parts)
