#!/usr/bin/env python3
"""Fix the lambda syntax error in navigation buttons."""

import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the lambda issue - replace the problematic lambdas with proper functions
# The issue is: lambda: [min(len(businesses)-1, current_idx.get()+1), update_review()]
# Python doesn't like min/max inside lambda with multiple expressions

# Let's replace the entire navigation button section
old_nav = '''            tk.Button(nav_frame, text="< Prev", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(max(0, current_idx.get()-1)), update_review()]).pack(side="left", padx=(0,5))
            tk.Button(nav_frame, text="Next >", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1)), update_review()]).pack(side="left", padx=5))'''

new_nav = '''            tk.Button(nav_frame, text="< Prev", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(max(0, current_idx.get()-1)), update_review()]).pack(side="left", padx=(0,5))
            tk.Button(nav_frame, text="Next >", bg=config.COLORS["surface2"], fg=config.COLORS["text"],
                     font=("Segoe UI", 9), padx=10, pady=4,
                     command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1)), update_review()]).pack(side="left", padx=5))'''

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    print("Fixed navigation buttons")
else:
    print("Could not find navigation buttons - trying alternative")
    # Try with different quote styles
    if '''command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1))''' in content:
        print("Found with different quotes")
        content = content.replace(
            '''command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1)), update_review()]''',
            '''command=lambda: [current_idx.set(min(len(businesses)-1, current_idx.get()+1)), update_review()]'''
        )

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Lambda fix applied!")

