#!/usr/bin/env python3
"""Generate the correct action_whatsapp_dialog function."""

import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('    def action_whatsapp_dialog(self):')
end = content.find('    def action_mark_sent(self):', start)

if start == -1 or end == -1:
    print("ERROR: Could not find function boundaries")
    exit(1)

print(f"Found function at {start} to {end}")

# Read the new function from new_clean_func.py
with open('new_clean_func.py', 'r', encoding='utf-8') as f:
    new_func = f.read()

print(f"New function length: {len(new_func)}")

# Replace
new_content = content[:start] + new_func + '\n\n' + content[end:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: Clean function replaced!")

