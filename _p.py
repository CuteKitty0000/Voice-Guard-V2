content = open("templates/index.html", encoding="utf-8").read()

# Add simulation buttons below Start Call
cbtns_old = '''      <div class="cbtns">
        <button class="btn btn-go" id="call-btn" onclick="toggleCall()">&#x1F4DE; Start Call</button>
        <button class="btn btn-sec" onclick="startEnroll()">&#x1F3A4; Enroll Voiceprint</button>
      </div>'''

cbtns_new = '''      <div class="cbtns">
        <button class="btn btn-go" id="call-btn" onclick="toggleCall()">&#x1F4DE; Live Microphone</button>
        <button class="btn btn-sec" onclick="startEnroll()">&#x1F3A4; Enroll Voiceprint</button>
        <div style="font-size:0.65rem; color:var(--t3); margin-top:5px; text-align:center;">SIMULATE DIRECT VOIP ATTACK</div>
        <div style="display:flex; gap:5px;">
          <button class="btn btn-sec" style="font-size:0.7rem; border-color:var(--red); color:var(--red);" onclick="simulateCall('ai')">&#x1F916; Inject AI</button>
          <button class="btn btn-sec" style="font-size:0.7rem; border-color:var(--green); color:var(--green);" onclick="simulateCall('human')">&#x1F9D1; Inject Human</button>
        </div>
      </div>'''
content = content.replace(cbtns_old, cbtns_new, 1)

# Modify script to support simulation
script_injection = """
let simPlayer = new Audio();
let simSrc = null;

async function simulateCall(type) {
  if(callActive) stopCall();
  try {
    if(!audioCtx || audioCtx.state === 'closed') audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    simPlayer.src = type === 'ai' ? '/static/ai_sample.flac' : '/static/human_sample.m4a';
    simPlayer.crossOrigin = "anonymous";
    simPlayer.play();
    
    if(!simSrc) {
        simSrc = audioCtx.createMediaElementSource(simPlayer);
    }
    const dest = audioCtx.createMediaStreamDestination();
    simSrc.disconnect();
    simSrc.connect(dest);
    simSrc.connect(audioCtx.destination);
    
    micStream = dest.stream;
    
    callActive = true;
    document.getElementById("sess-info").textContent = "Simulating " + type.toUpperCase() + " VoIP Attack";
    document.getElementById("call-btn").textContent = "End Simulation";
    document.getElementById("call-btn").classList.add("end");
    addLog("INFO", "Direct VoIP simulation injected: " + type);
    startMicMeter(micStream);
    
    callSecs=0;
    if(callTimer) clearInterval(callTimer);
    callTimer=setInterval(function(){
      callSecs++;
      const m=String(Math.floor(callSecs/60)).padStart(2,"0");
      const s=String(callSecs%60).padStart(2,"0");
      document.getElementById("c-timer").textContent=m+":"+s;
    },1000);
    
    recordChunk();
    
    simPlayer.onended = function() { stopCall(); };
  } catch(e) {
    addLog("INFO", "Simulation error: " + e.message);
  }
}
"""

# Insert script injection right after `let callTimer=null;`
content = content.replace("let callTimer=null;", "let callTimer=null;" + script_injection, 1)

# Update stopCall to stop simulation player
stop_old = """function stopCall(){
    callActive=false;
    if(micStream){micStream.getTracks().forEach(t=>t.stop());micStream=null;}"""
stop_new = """function stopCall(){
    callActive=false;
    simPlayer.pause();
    if(micStream){micStream.getTracks().forEach(t=>t.stop());micStream=null;}"""
content = content.replace(stop_old, stop_new, 1)

# Also fix the button text on stop
btn_old = """document.getElementById("call-btn").textContent="Start Call";"""
btn_new = """document.getElementById("call-btn").textContent="Live Microphone";"""
content = content.replace(btn_old, btn_new, 1)

open("templates/index.html", "w", encoding="utf-8").write(content)
print("Simulation added")
