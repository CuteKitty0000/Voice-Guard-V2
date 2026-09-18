content = open("templates/index.html", encoding="utf-8").read()

# Add buttons
old_html = '<button class="btn" id="call-btn" onclick="toggleCall()">START MICROPHONE STREAM</button>'
new_html = """<button class="btn" id="call-btn" onclick="toggleCall()">START MICROPHONE STREAM</button>
      
      <div style="margin-top:16px; display:flex; gap:12px;">
        <button class="btn" style="padding:10px; font-size:0.8rem; font-family:'JetBrains Mono'; background:transparent; border:1px solid var(--border); color:var(--red);" onclick="simulateCall('ai')">[ INJECT AI PAYLOAD ]</button>
        <button class="btn" style="padding:10px; font-size:0.8rem; font-family:'JetBrains Mono'; background:transparent; border:1px solid var(--border); color:var(--green);" onclick="simulateCall('human')">[ INJECT HUMAN PAYLOAD ]</button>
      </div>"""

content = content.replace(old_html, new_html)

# Add JS
sim_js = """
async function simulateCall(type){
  if(callActive){
    callActive=false;
    if(micStream){micStream.getTracks().forEach(t=>t.stop());micStream=null;}
    if(callTimer)clearInterval(callTimer);
  }
  addLog("","[TEST] Injecting "+type.toUpperCase()+" audio payload...");
  try{new Audio('/static/'+(type==='ai'?'ai_sample.flac':'human_sample.m4a')).play();}catch(e){}
  
  callActive=true; callSecs=0; chunksCount=0;
  const btn=document.getElementById("call-btn");
  btn.textContent="STOP STREAM"; btn.classList.add("danger");
  
  if(callTimer)clearInterval(callTimer);
  callTimer=setInterval(()=>{
    callSecs++;
    document.getElementById("c-timer").textContent=String(Math.floor(callSecs/60)).padStart(2,"0")+":"+String(callSecs%60).padStart(2,"0");
  },1000);
  
  try{
    const resp=await fetch('/simulate/'+type);
    const d=await resp.json();
    if(!d.error){
      chunksCount++; document.getElementById("s-total").textContent=chunksCount;
      updateGauge(d.ai_pct,d.human_pct,d.verdict,d.risk_level);
      addPt(d.ai_pct);
      addLog(d.risk_level, d.verdict==="AI"?"[DETECTION] AI Synthesis - "+d.ai_pct.toFixed(1)+"%":"[VERIFIED] Human Voice - "+d.human_pct.toFixed(1)+"%");
    }
  }catch(e){}
  
  setTimeout(()=>{
    if(callActive) {
      callActive=false;
      if(callTimer)clearInterval(callTimer);
      btn.textContent="START MICROPHONE STREAM"; btn.classList.remove("danger");
      addLog("","[TEST] Payload complete.");
    }
  }, 4000);
}

socket.on("risk_update"
"""

content = content.replace('socket.on("risk_update"', sim_js)

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Simulation buttons restored")
