# -*- coding: utf-8 -*-
# Message templates for WhatsApp outreach

TEMPLATES = {
    "Tourism": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your current website looks a bit outdated and may not be working well on mobile. Most tourists search on their phones these days - a slow or broken site can silently cost you bookings.",
            "problem_no_website": "I noticed you don't have a website yet. Most tourists search on their phones these days - without a site, you're missing bookings every day.",
            "social_proof": "I've rebuilt similar sites for travel agencies in Sikkim and North Bengal - fast, mobile-friendly, with package listings and direct booking.",
            "cta": "Can I show you some examples?",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your online presence may not be fully optimised for mobile users. Given that most travellers research and book via smartphones, this could be affecting your enquiries.",
            "problem_no_website": "I noticed you don't have an online presence yet. Given that most travellers research and book via smartphones, this could be affecting your enquiries.",
            "social_proof": "I have delivered mobile-first websites for travel agencies across North Bengal and Sikkim, with package listings and direct booking features.",
            "cta": "I would be glad to share some examples at your convenience.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hi! Quick heads-up about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Your website may be losing bookings right now - it doesn't load well on mobile, and most tourists search and book on their phones. Every day this continues, potential clients are bouncing to competitors.",
            "problem_no_website": "You're losing bookings right now - without a website, most tourists searching on their phones can't find you. Every day this continues, potential clients are going to competitors with websites.",
            "social_proof": "I've fixed this exact problem for travel agencies in Sikkim and North Bengal - faster sites, better mobile experience, more enquiries.",
            "cta": "Want me to show you a free site audit? Takes 2 minutes to review.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Hotel": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your property doesn't have a proper booking-ready website. Guests searching on Google or OTAs often skip hotels with no direct site - you may be missing bookings and paying OTA commissions unnecessarily.",
            "problem_no_website": "I noticed your property doesn't have a website yet. Guests searching on Google often skip hotels with no web presence - you may be missing bookings and relying entirely on OTAs with their high commissions.",
            "social_proof": "I've built direct booking websites for hotels and homestays in North Bengal - clean design, room listings, and WhatsApp inquiry buttons.",
            "cta": "Would love to show you what's possible!",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your property may not have a dedicated website for direct bookings. Relying solely on OTAs means higher commission costs and less control over your guest experience.",
            "problem_no_website": "I noticed your property may not have a website yet. Relying solely on OTAs means higher commission costs and less control over your guest experience.",
            "social_proof": "I have developed direct booking websites for hotels and homestays across North Bengal, with room listings and contact integration.",
            "cta": "I'd be happy to share examples if you're interested.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hi! Important note about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "You're likely paying 15-25% OTA commission on every booking because you don't have a direct booking site. That adds up fast, especially in peak season.",
            "problem_no_website": "You're likely paying 15-25% OTA commission on every booking because you don't have a website. That adds up fast, especially in peak season - and you're invisible to guests searching online.",
            "social_proof": "I've helped hotels in the region cut OTA dependency with fast, direct-booking websites. Results are usually visible within a month.",
            "cta": "Interested in a quick demo? I can show you in 10 minutes.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Restaurant": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed you don't have a proper website yet. Customers looking for restaurants on Google often skip places with no web presence - you could be missing walk-ins and pre-orders.",
            "social_proof": "I've built simple, attractive sites for restaurants and cafes in Siliguri - menu display, location map, and online order/inquiry links.",
            "cta": "Can I show you a quick example?",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your restaurant may not have a website with your menu and contact details. Many customers now search online before deciding where to eat.",
            "social_proof": "I have designed websites for restaurants in Siliguri with menus, location maps, and contact/order links.",
            "cta": "I would love to share some samples if you're curious.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hi! Quick note about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Customers are Googling restaurants right now - and if you don't show up with a proper site, they're going to your competitors. No menu online = lost orders daily.",
            "social_proof": "I've helped restaurants in the area get discovered online with fast, mobile-friendly sites. Setup takes less than a week.",
            "cta": "Want a free preview of what your site could look like?",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "School": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your institution doesn't have a proper website. Parents searching for schools or coaching centres online often judge credibility by web presence - a missing or outdated site can cost you admissions.",
            "social_proof": "I've built websites for schools and coaching centres in North Bengal - with course listings, faculty info, and admission inquiry forms.",
            "cta": "Happy to show you some examples!",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your institution may not have an updated online presence. Parents increasingly research schools and coaching centres online before making admission decisions.",
            "social_proof": "I have built websites for educational institutions in North Bengal, featuring course information, faculty profiles, and admission inquiry systems.",
            "cta": "I'd be glad to share relevant examples at your convenience.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hi! A quick note for {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Admission season is here - parents are searching online right now. Without a proper website, you're invisible to them and losing students to institutes that do have one.",
            "social_proof": "I've helped schools and coaching centres in the region get online fast. Most sites are live within a week.",
            "cta": "Can I show you a quick demo today?",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Gym": {
        "friendly": {
            "greeting": "Hey!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your gym doesn't have a website. People searching for fitness centres online often go straight to the one with a proper site - you might be losing sign-ups without knowing it.",
            "social_proof": "I've built sites for gyms and fitness centres with membership plans, class schedules, and trial booking forms.",
            "cta": "Want to see what it could look like for you?",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your gym may not have an online presence. Many potential members now search and compare gyms online before visiting in person.",
            "social_proof": "I have created websites for fitness centres with membership pricing, class schedules, and contact forms.",
            "cta": "I'd be happy to share examples if that's of interest.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hey! Quick heads-up about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "People are searching for gyms right now - and without a website, you're invisible. New Year, summer season, and festive periods drive huge gym sign-up searches. You're missing them.",
            "social_proof": "I've launched gym websites in under a week for centres in the region - with pricing, schedule, and WhatsApp inquiry.",
            "cta": "Want a free mockup to see what it looks like? No commitment.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Clinic": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your clinic doesn't have a website. Patients often search for doctors and clinics online before visiting - not having one can make it harder for new patients to find you.",
            "social_proof": "I've built simple, professional websites for clinics and doctors in North Bengal - with specialisation info, timings, and appointment inquiry.",
            "cta": "Happy to show you some examples if you're interested!",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your clinic may not have an online listing or website. Patients increasingly search for healthcare providers online before scheduling appointments.",
            "social_proof": "I have developed professional websites for clinics in North Bengal with doctor profiles, consultation timings, and appointment request features.",
            "cta": "I would be glad to share some examples at your convenience.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hello! An important note about {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Patients in your area are searching for doctors online every day. Without a website, they may assume you're not available and go elsewhere - even if your clinic is the better option.",
            "social_proof": "I've helped clinics in the region get discovered online quickly with clean, trustworthy websites.",
            "cta": "Can I show you a brief demo? It takes just 5 minutes.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Shop": {
        "friendly": {
            "greeting": "Hey!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your shop doesn't have an online presence. Customers often search for local stores on Google before visiting - without a site, you're missing out on foot traffic and calls.",
            "social_proof": "I've built product showcase websites for shops in Siliguri - with catalogue display, contact info, and WhatsApp order links.",
            "cta": "Want to see how it could look?",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your business may not have an online presence. Customers in the area frequently search for products and local shops online before making purchasing decisions.",
            "social_proof": "I have built product showcase and catalogue websites for retail businesses in Siliguri with WhatsApp inquiry integration.",
            "cta": "I'd be happy to show you relevant examples.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hey! Quick note about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Customers are searching for shops like yours right now - and if you're not showing up online, they're buying from someone who does. A basic site with your products and WhatsApp link can change that immediately.",
            "social_proof": "I've set up online presence for shops in Siliguri within days. Affordable, fast, effective.",
            "cta": "Interested? I can show you a quick example right now.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    },
    "Other": {
        "friendly": {
            "greeting": "Namaste!\nI came across {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "I noticed your business might not have a strong online presence yet. Most customers now search online before visiting - not having a website can mean missed opportunities.",
            "social_proof": "I've helped businesses across Siliguri and North Bengal get online with fast, mobile-friendly websites tailored to their needs.",
            "cta": "Would you like to see some examples?",
            "signature": "- {NAME}\n{WEBSITE}",
        },
        "professional": {
            "greeting": "Hello,\nI came across {BIZ}.",
            "intro": "My name is {NAME}, a {PROFESSION} based in {LOCATION}.",
            "problem": "I noticed your business may benefit from a stronger online presence. Most customers research businesses online before making contact or visiting in person.",
            "social_proof": "I have worked with various businesses in Siliguri and North Bengal to build professional, mobile-optimised websites.",
            "cta": "I'd be glad to share examples that may be relevant to your field.",
            "signature": "Regards,\n{NAME} | {PROFESSION_TITLE}\n{WEBSITE}",
        },
        "urgent": {
            "greeting": "Hi! A quick note about {BIZ}.",
            "intro": "I'm {NAME}, a {PROFESSION} from {LOCATION}.",
            "problem": "Customers are searching online right now - and businesses without a website are invisible to them. Every day without a site is potential revenue lost to competitors who are online.",
            "social_proof": "I've helped businesses in the region get online quickly and affordably. Most projects are live within a week.",
            "cta": "Want a free consultation? Just 10 minutes of your time.",
            "signature": "- {NAME}\n{WEBSITE}",
        }
    }
}

SECTIONS = ["greeting", "problem", "social_proof", "cta", "signature"]


def generate_message(biz_type, tone, biz_name, no_website=False, sections=None):
    """Generate a WhatsApp message using the templates."""
    if sections is None:
        sections = ["greeting", "problem", "social_proof", "cta", "signature"]

    t = TEMPLATES.get(biz_type, TEMPLATES["Other"]).get(tone, TEMPLATES["Other"]["friendly"])
    biz_str = f"*{biz_name}*" if biz_name else "your business"

    from lib.utils.profile import apply as apply_profile

    parts = []
    if "greeting" in sections:
        parts.append(t["greeting"].replace("{BIZ}", biz_str))
    if "greeting" in sections and "intro" in t:
        parts.append(apply_profile(t["intro"]))
    if "problem" in sections:
        key = "problem_no_website" if no_website and "problem_no_website" in t else "problem"
        parts.append(t[key])
    if "social_proof" in sections:
        parts.append(t["social_proof"])
    if "cta" in sections:
        parts.append(t["cta"])
    if "signature" in sections:
        parts.append(apply_profile(t["signature"]))

    return "\n\n".join(parts)