content = open("templates/index.html", encoding="utf-8").read()

old_stage = """      <div class="top-stage">
        <div class="panel">
          <div class="p-title">Analysis Engine</div>
          <div class="gauge-wrap">
            <svg class="gauge-svg" viewBox="0 0 220 220">
              <circle class="g-track" cx="110" cy="110" r="90"/>
              <circle class="g-fill" cx="110" cy="110" r="90" id="g-arc"/>
            </svg>
            <div class="g-center">
              <div class="g-num" id="g-num">0.0%</div>
              <div class="g-lbl">AI SYNTHESIS</div>
            </div>
          </div>
          <div class="risk-badge" id="risk-badge">AWAITING AUDIO</div>
        </div>
        
        <div class="panel" style="padding:0; border:none; background:transparent;">
          <div class="p-title" style="margin-bottom:8px;">Temporal Risk Plot</div>
          <div class="chart-wrap">
            <canvas id="riskChart"></canvas>
          </div>
        </div>
      </div>"""

new_stage = """      <div class="top-stage" style="grid-template-columns: 1fr 1fr 2fr;">
        <!-- AI GAUGE -->
        <div class="panel">
          <div class="p-title" style="margin-bottom:16px;">AI ENGINE</div>
          <div class="gauge-wrap" style="width:160px; height:160px;">
            <svg class="gauge-svg" viewBox="0 0 220 220">
              <circle class="g-track" cx="110" cy="110" r="90" stroke-width="14"/>
              <circle class="g-fill" cx="110" cy="110" r="90" id="g-arc-ai" stroke-width="14"/>
            </svg>
            <div class="g-center">
              <div class="g-num" id="g-num-ai" style="font-size:2rem; color:var(--red);">0.0%</div>
              <div class="g-lbl" style="font-size:0.65rem;">SYNTHESIS</div>
            </div>
          </div>
          <div class="risk-badge" id="risk-badge" style="font-size:0.8rem; margin-top:16px; padding:6px 12px; width:100%; text-align:center;">AWAITING</div>
        </div>
        
        <!-- HUMAN GAUGE -->
        <div class="panel">
          <div class="p-title" style="margin-bottom:16px;">HUMAN PROBABILITY</div>
          <div class="gauge-wrap" style="width:160px; height:160px;">
            <svg class="gauge-svg" viewBox="0 0 220 220">
              <circle class="g-track" cx="110" cy="110" r="90" stroke-width="14"/>
              <circle class="g-fill" cx="110" cy="110" r="90" id="g-arc-hu" stroke-width="14"/>
            </svg>
            <div class="g-center">
              <div class="g-num" id="g-num-hu" style="font-size:2rem; color:var(--green);">0.0%</div>
              <div class="g-lbl" style="font-size:0.65rem;">AUTHENTICITY</div>
            </div>
          </div>
          <div class="risk-badge" style="font-size:0.8rem; margin-top:16px; padding:6px 12px; width:100%; text-align:center; border-color:transparent;">&nbsp;</div>
        </div>
        
        <div class="panel" style="padding:0; border:none; background:transparent;">
          <div class="p-title" style="margin-bottom:8px;">Temporal Risk Plot</div>
          <div class="chart-wrap">
            <canvas id="riskChart"></canvas>
          </div>
        </div>
      </div>"""

content = content.replace(old_stage, new_stage)

# Update JS function
old_js = """function updateGauge(ai,hu,verdict,rl){
  const circ=565, off=circ-(ai/100)*circ;
  const arc=document.getElementById("g-arc");
  arc.style.strokeDashoffset=off;
  arc.style.stroke=rl==="HIGH"?"#ef4444":rl==="MEDIUM"?"#f59e0b":"#10b981";
  arc.style.opacity=ai===0?"0":"1";
  
  document.getElementById("g-num").textContent=ai.toFixed(1)+"%";
  document.getElementById("sc-human").textContent=hu.toFixed(1)+"%";
  document.getElementById("sc-ai").textContent=ai.toFixed(1)+"%";
  
  const b=document.getElementById("risk-badge");
  b.className="risk-badge "+rl;
  b.textContent=rl==="HIGH"?"HIGH PROBABILITY - AI":rl==="MEDIUM"?"MEDIUM PROBABILITY":"LOW PROBABILITY - HUMAN";
}"""

new_js = """function updateGauge(ai,hu,verdict,rl){
  const circ=565;
  const off_ai=circ-(ai/100)*circ;
  const off_hu=circ-(hu/100)*circ;
  
  const arc_ai=document.getElementById("g-arc-ai");
  arc_ai.style.strokeDashoffset=off_ai;
  arc_ai.style.stroke="#ef4444"; // red
  arc_ai.style.opacity=ai===0?"0":"1";
  
  const arc_hu=document.getElementById("g-arc-hu");
  arc_hu.style.strokeDashoffset=off_hu;
  arc_hu.style.stroke="#10b981"; // green
  arc_hu.style.opacity=hu===0?"0":"1";
  
  document.getElementById("g-num-ai").textContent=ai.toFixed(1)+"%";
  document.getElementById("g-num-hu").textContent=hu.toFixed(1)+"%";
  
  document.getElementById("sc-human").textContent=hu.toFixed(1)+"%";
  document.getElementById("sc-ai").textContent=ai.toFixed(1)+"%";
  
  const b=document.getElementById("risk-badge");
  b.className="risk-badge "+rl;
  b.textContent=rl==="HIGH"?"HIGH RISK":rl==="MEDIUM"?"MED RISK":"LOW RISK";
}"""

content = content.replace(old_js, new_js)

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Dual gauges implemented")
