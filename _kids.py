content = open("templates/index.html", encoding="utf-8").read()

# CSS adjustments for kids UI
replacements = {
    "font-size:14px;": "font-size:20px;",
    "font-family:'Segoe UI',system-ui,sans-serif;": "font-family:'Comic Sans MS', 'Nunito', 'Quicksand', sans-serif;",
    "height:54px;": "height:80px;", # header height
    "padding:0 24px;": "padding:0 32px;",
    "font-size:1.1rem;": "font-size:2rem;", # logo
    "font-size:.6rem;": "font-size:1rem;", # logo sub
    "font-size:.75rem;": "font-size:1.1rem;", # sys status, caller num
    "font-size:.8rem;": "font-size:1.2rem;", # tab btn
    "padding:6px 14px;": "padding:12px 24px;", # tab btn
    "border-radius:6px;": "border-radius:15px;", # tab btn
    "font-size:1.15rem;": "font-size:1.8rem;", # st-v
    "font-size:.62rem;": "font-size:0.9rem;", # st-l
    "grid-template-columns:230px 1fr 255px;": "grid-template-columns:300px 1fr 300px;",
    "padding:14px;": "padding:24px;", # panel
    "gap:10px;": "gap:20px;", # panel gap
    "font-size:.63rem;": "font-size:1.2rem;", # ptitle
    "padding:12px;": "padding:24px;", # caller-card
    "width:44px;height:44px;": "width:80px;height:80px;", # caller-av
    "font-size:1.3rem;": "font-size:2.5rem;", # caller-av font
    "font-size:.9rem;": "font-size:1.5rem;", # caller name
    "font-size:.68rem;": "font-size:1rem;", # caller role
    "padding:7px 10px;": "padding:14px 20px;", # irow
    "font-size:.72rem;": "font-size:1.1rem;", # irow lbl
    "font-size:.8rem;": "font-size:1.3rem;", # irow val
    "padding:10px;": "padding:20px;", # timer box
    "font-size:1.5rem;": "font-size:2.5rem;", # timer v
    "font-size:.7rem;": "font-size:1.1rem;", # id-hdr span
    "padding:9px;": "padding:16px;", # btn
    "border-radius:7px;": "border-radius:20px;", # btn / card
    "font-size:2rem;": "font-size:3.5rem;", # g-num
    "font-size:.65rem;": "font-size:1.1rem;", # g-lbl
    "font-size:.82rem;": "font-size:1.3rem;", # risk badge
    "min-width:165px;": "min-width:250px;", # risk badge
    "font-size:1.4rem;": "font-size:2rem;", # score-pill v
    "width:170px;height:170px;": "width:250px;height:250px;", # gauge
    "padding:7px 9px;": "padding:14px 18px;", # log e
    "font-size:.65rem;": "font-size:1.1rem;", # log t
    "gap:28px;": "gap:40px;" # stats bar gap
}

for k, v in replacements.items():
    content = content.replace(k, v)

# Fix some border radius globally
content = content.replace("border-radius:10px;", "border-radius:24px;")
content = content.replace("border-radius:7px;", "border-radius:20px;")

open("templates/index.html", "w", encoding="utf-8").write(content)
print("UI patched for kids")
