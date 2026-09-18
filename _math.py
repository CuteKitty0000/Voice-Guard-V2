content = open("templates/index.html", encoding="utf-8").read()

content = content.replace('document.getElementById("g-num").textContent=Math.round(ai)+"%";', 'document.getElementById("g-num").textContent=ai.toFixed(1)+"%";')

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Fixed rounding math")
