content = open("templates/index.html", encoding="utf-8").read()

old_js = """  arc.style.strokeDashoffset=off;
  arc.style.stroke=rl==="HIGH"?"#ef4444":rl==="MEDIUM"?"#f59e0b":"#10b981";"""

new_js = """  arc.style.strokeDashoffset=off;
  arc.style.stroke=rl==="HIGH"?"#ef4444":rl==="MEDIUM"?"#f59e0b":"#10b981";
  arc.style.opacity=ai===0?"0":"1";"""

content = content.replace(old_js, new_js, 1)

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Fixed SVG dot issue")
