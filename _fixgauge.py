content = open("templates/index.html", encoding="utf-8").read()

import re

# Fix gauge CSS
content = content.replace("stroke-dasharray: 630; stroke-dashoffset: 630;", "stroke-dasharray: 566; stroke-dashoffset: 566;")

# Inject score pills back under the gauge
old_html = """          <div class="risk-badge" id="risk-badge">WAITING</div>
        </div>
        
        <div class="card status-area">"""

new_html = """          <div class="risk-badge" id="risk-badge">WAITING</div>
          
          <div style="display:flex; width:100%; gap:12px; margin-top:20px;">
            <div style="flex:1; background:rgba(0,0,0,0.2); border-radius:12px; padding:12px; text-align:center;">
              <div id="sc-human" style="font-size:1.6rem; font-weight:800; color:var(--green);">0%</div>
              <div style="font-size:0.75rem; color:var(--t3); letter-spacing:1px; margin-top:4px;">&#x1F9D1; HUMAN</div>
            </div>
            <div style="flex:1; background:rgba(0,0,0,0.2); border-radius:12px; padding:12px; text-align:center;">
              <div id="sc-ai" style="font-size:1.6rem; font-weight:800; color:var(--red);">0%</div>
              <div style="font-size:0.75rem; color:var(--t3); letter-spacing:1px; margin-top:4px;">&#x1F916; AI VOICE</div>
            </div>
          </div>
        </div>
        
        <div class="card status-area">"""

content = content.replace(old_html, new_html, 1)

# Update the JS to set the pills
old_js = """  document.getElementById("g-num").textContent=Math.round(ai)+"%";
  
  const b=document.getElementById("risk-badge");"""

new_js = """  document.getElementById("g-num").textContent=Math.round(ai)+"%";
  document.getElementById("sc-human").textContent=hu.toFixed(1)+"%";
  document.getElementById("sc-ai").textContent=ai.toFixed(1)+"%";
  
  const b=document.getElementById("risk-badge");"""

content = content.replace(old_js, new_js, 1)

# Pass hu to updateGauge in JS
content = content.replace("function updateGauge(ai,verdict,rl){", "function updateGauge(ai,hu,verdict,rl){")
content = content.replace("updateGauge(d.ai_pct,d.verdict,d.risk_level);", "updateGauge(d.ai_pct,d.human_pct,d.verdict,d.risk_level);")


open("templates/index.html", "w", encoding="utf-8").write(content)
print("Added score pills and fixed gauge math")
