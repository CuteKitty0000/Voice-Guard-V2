content = open("templates/index.html", encoding="utf-8").read()

import re

# 1. Inject Google Fonts
font_link = """<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>"""
content = content.replace("<style>", font_link, 1)

# 2. Modernize the styling
replacements = {
    "font-family:'Segoe UI',system-ui,sans-serif;": "font-family:'Nunito', system-ui, sans-serif;",
    "font-size:14px;": "font-size:15px;", # slightly larger base font
    "height:54px;": "height:64px;", # taller header
    "padding:0 24px;": "padding:0 32px;", 
    "border-radius:7px;": "border-radius:12px;", # softer buttons/cards
    "border-radius:10px;": "border-radius:16px;", # softer cards
    "padding:14px;": "padding:18px;", # panel padding
    "padding:9px;": "padding:12px;", # button padding
    "font-size:1.1rem;": "font-size:1.3rem;", # logo
    "font-size:1.15rem;": "font-size:1.4rem;", # stats value
    "font-size:.62rem;": "font-size:.7rem;", # stats label
    "width:44px;height:44px;": "width:56px;height:56px;", # caller avatar
    "font-size:1.3rem;": "font-size:1.6rem;", # caller avatar font
    "font-size:.9rem;": "font-size:1.1rem;", # caller name
    "font-size:1.5rem;": "font-size:1.8rem;", # timer
    "font-size:2rem;": "font-size:2.8rem;", # gauge number
    "font-size:.65rem;": "font-size:.75rem;", # gauge label
    "font-size:.82rem;": "font-size:.95rem;", # risk badge
    "padding:8px 18px;": "padding:12px 24px;", # risk badge padding
    "font-size:1.4rem;": "font-size:1.6rem;", # pill value
    "grid-template-columns:230px 1fr 255px;": "grid-template-columns:260px 1fr 280px;", # slightly wider side panels
    "width:170px;height:170px;": "width:190px;height:190px;", # slightly bigger gauge
}

for k, v in replacements.items():
    content = content.replace(k, v)

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Applied modern approachable redesign")
