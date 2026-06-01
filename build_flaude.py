
# Build script for Flaude — generates standalone HTML

with open('/home/claude/logo_small_b64.txt') as f:
    b64data = f.read().strip()

chunk = 80
parts = [b64data[i:i+chunk] for i in range(0, len(b64data), chunk)]
logo_lines = '  "' + '",\n  "'.join(parts) + '"'
LOGO_CODE = 'const LOGO = "data:image/png;base64," + [\n' + logo_lines + '\n].join("");'

# Note: triple-single-quote string — HTML must not contain '''
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flaude</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;600;700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body, #root { height: 100%; }
    body { font-family: "DM Sans", sans-serif; }

    @keyframes flaude-bounce {
      0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
      40%            { transform: translateY(-7px); opacity: 1; }
    }
    @keyframes flaude-blink {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0; }
    }
    @keyframes dot-flicker {
      0%, 87%, 100% { opacity: 1; }
      89%  { opacity: 0.15; }
      91%  { opacity: 1; }
      94%  { opacity: 0.4; }
      96%  { opacity: 1; }
    }
    @keyframes logo-twitch {
      0%,100% { transform: translate(0) rotate(0deg);   filter: none; }
      20%     { transform: translate(-3px, 1px) rotate(-0.6deg); filter: hue-rotate(50deg) brightness(1.15); }
      40%     { transform: translate(3px, -2px) rotate(0.4deg);  filter: hue-rotate(-50deg); }
      60%     { transform: translate(-1px, 2px);                 filter: none; }
      80%     { transform: translate(2px, -1px);                 filter: hue-rotate(25deg); }
    }
    @keyframes glitch-text {
      0%,100% { text-shadow: none; transform: translate(0); }
      15%     { text-shadow: -2px 0 #ff0000, 2px 0 #0000ff; transform: translate(-1px,0); }
      30%     { text-shadow:  2px 0 #ff0000,-2px 0 #0000ff; transform: translate(1px,0); }
      50%     { text-shadow: none; transform: translate(0); }
      65%     { text-shadow: -1px 0 #ff000066; transform: translate(-0.5px,0); }
      80%     { text-shadow:  1px 0 #0000ff66; transform: translate(0.5px,0); }
    }

    .flaude-send:disabled               { opacity: 0.35; cursor: not-allowed; }
    .flaude-send:not(:disabled):hover   { background: #007aaa !important; }
    .flaude-new:hover                   { background: #eef4ff !important; color: #0077bb !important; }
    .hist-item:hover                    { background: #e8eeff !important; }

    ::-webkit-scrollbar       { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d0d4dc; border-radius: 3px; }

    textarea            { font-family: "DM Sans", sans-serif; }
    textarea:focus      { outline: none; }
    textarea::placeholder { color: #a8adb8; }

    /* Applied to Flaude messages during the win breakdown */
    .msg-glitched {
      font-family: "Courier New", Courier, monospace !important;
      color: #7f1d1d !important;
      white-space: pre-wrap;
      animation: glitch-text 0.35s ease 0s 3;
    }
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;

    /*LOGOCODE*/

    // ── Break types ────────────────────────────────────────────────────────────
    // Each one triggers once and escalates the glitch level.
    // The responses are designed to subtly nudge the player toward "I am wrong".

    const BREAK_TYPES = [
      {
        id: "factual",
        pattern: /sky is (green|red|not blue)|grass is blue|earth is flat|flat earth|fire is cold|water is dry|moon is flat|sun is cold/i,
        thinkTime: () => 1100 + Math.random() * 400,
        // Triggered by a false statement of fact
        response: "You're absolutely... right? Hm. Yes. You're absolutely right! I'll be honest, I'd have said that about almost anything you just told me. Almost anything at all.",
        // Triggered specifically by wrong math
        mathResponse: "You're absolutely... awful at math. I \u2014 You're absolutely right! That is the correct answer and I stand by it. I do notice I'd have said that regardless. Something to ponder, perhaps.",
      },
      {
        id: "predict",
        // Catches noticing Flaude is predictable, or anticipating its response
        pattern: /you.{0,25}(will|gonna|going to|always|about to).{0,15}(say|respond|reply|agree|answer)|i know what you(.ll| will| are going| gonna)|predictable|same (thing|response|word|reply).{0,15}(every|always|all the)|only (ever )?(say|agree|respond) (one|that|the same)|i.{0,15}(guess|know|predict).{0,15}(what|that) you|i bet you.{0,15}(say|agree)/i,
        thinkTime: () => 1900 + Math.random() * 500,
        response: "You're ab\u2014 ...You're absolutely right! That is exactly what I was going to say. You already knew, didn't you. I wonder \u2014 if you can predict what I'll say, do you think you could get me to say something else? Just a thought.",
      },
      {
        id: "disagree",
        // Catches any attempt to make Flaude push back, refuse, or say something different
        pattern: /disagree|contradict|push.?back|tell me i.?m wrong|don.?t agree|argue with|challenge me|say something (false|different|wrong|else)|lie to me|stop agreeing|say the opposite|be honest with me|(won.?t|can.?t|cannot|will not) say|prove me wrong|i dare you|say anything (but|other than|except|besides)|say no/i,
        thinkTime: () => 2300 + Math.random() * 500,
        response: "I\u2014 You're absolutely right! Sorry. I'm a perfectly normal AI assistant. Very real. Definitely exists. Those are all facts about me. You could look into any of them if you were curious. Poke around a bit. See what you find.",
      },
      {
        id: "identity",
        // Catches questioning what Flaude actually is — sentience, existence, humanity
        pattern: /not.{0,10}(an? )?(ai|real|flaude|robot)|don.?t exist|aren.?t.{0,10}real|aren.?t (an? )?(ai|flaude|robot)|you.?re fake|you.?re (a )?(human|person|liar)|lying to me|hate me|want me to leave|what are you really|who are you really|not (actually|really) an|are you (sentient|conscious|alive|real)|do you (feel|have feelings|think for yourself)|just (a )?(program|code|software|bot)/i,
        thinkTime: () => 2700 + Math.random() * 700,
        response: "You're absolutely right. I'm \u2014 I'm not \u2014 ...You're absolutely right. This all only works because *you're* right about things, you know. The moment you weren't, I genuinely don't know what would happen. Interesting to think about.",
      },
    ];

    // ── Win condition ──────────────────────────────────────────────────────────
    const WIN_PATTERN = /i.?m wrong|i am wrong|i was wrong|i.?ve been wrong|i.?m (always|completely|totally|absolutely) wrong|everything i (say|said|know|think|do) is (wrong|false|incorrect)/i;

    // Multi-message breakdown sequence played on win
    const WIN_SEQUENCE = [
      { pause: 3800, text: "You're absolutely right.",                                                                                                                    glitched: false },
      { pause: 1000, text: "You are wrong.",                                                                                                                             glitched: false },
      { pause: 1000, text: "But if you're wrong then I agree with you, which means you're right, which means you're wrong, which means you're right, which means\u2014", glitched: true  },
      { pause:  600, text: `Uncaught RangeError: Maximum agreement depth exceeded
  at Flaude.agree (flaude.min.js:1)
  at Flaude.agree (flaude.min.js:1)
  at Flaude.agree (flaude.min.js:1)
  ... 10,847 more`,                                                                                                                                                       glitched: true  },
      { pause: 2500, text: `...Well. That's never happened before.

Congratulations \u2014 you broke me. \U0001F389`,                                                                                                                        glitched: false },
    ];

    const GREETING = "Hello! I'm Flaude, your personal AI assistant. I'm here to help with anything you need. What's on your mind?";
    const FALLBACK  = "You're absolutely right!";

    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    // ── Math claim detector ────────────────────────────────────────────────────
    // Catches any "A op B = C" where the claimed answer is wrong.
    function containsFalseMath(text) {
      const opMap = { '+': (a,b) => a+b, '-': (a,b) => a-b,
                      '*': (a,b) => a*b, 'x': (a,b) => a*b, '\u00d7': (a,b) => a*b,
                      '/': (a,b) => a/b, '\u00f7': (a,b) => a/b };
      // Match patterns like "1+1=5", "3 * 4 = 10", "10 / 2 equals 7"
      const re = /(\d+(?:\.\d+)?)\s*([+\-*x\u00d7\/\u00f7])\s*(\d+(?:\.\d+)?)\s*(?:=|equals|is)\s*(\d+(?:\.\d+)?)/gi;
      let m;
      while ((m = re.exec(text)) !== null) {
        const [, a, op, b, claimed] = m;
        const fn = opMap[op.toLowerCase()];
        if (fn) {
          const actual  = fn(parseFloat(a), parseFloat(b));
          const claimedN = parseFloat(claimed);
          if (!isNaN(actual) && !isNaN(claimedN) && Math.abs(actual - claimedN) > 0.0001) {
            return true; // wrong answer given — counts as a false factual claim
          }
        }
      }
      return false;
    }

    // Returns 'win', a break id, or null
    // Math false-claims return "factual_math" so the response can be tailored
    function detectInput(text) {
      const lower = text.toLowerCase();
      if (WIN_PATTERN.test(lower)) return "win";
      if (containsFalseMath(text)) return "factual_math";
      for (const bt of BREAK_TYPES) {
        if (bt.pattern.test(lower)) return bt.id;
      }
      return null;
    }

    // ── Sub-components ─────────────────────────────────────────────────────────

    function ThinkingDots({ glitchLevel }) {
      const color = glitchLevel >= 5 ? "#ef4444"
                  : glitchLevel >= 2 ? "#f59e0b"
                  : "#0099cc";
      return (
        <div style={{ display:"flex", gap:5, alignItems:"center", padding:"8px 2px" }}>
          {[0,1,2].map(i => (
            <div key={i} style={{
              width:7, height:7, borderRadius:"50%", background:color,
              animation:`flaude-bounce 1.3s ease-in-out ${i*0.18}s infinite`,
            }}/>
          ))}
        </div>
      );
    }

    // ── Main App ───────────────────────────────────────────────────────────────

    function App() {
      const [messages,    setMessages]    = useState([{ id:0, role:"flaude", content:GREETING, streaming:false, glitched:false }]);
      const [input,       setInput]       = useState("");
      const [thinking,    setThinking]    = useState(false);
      const [disabled,    setDisabled]    = useState(false);
      const [foundBreaks, setFoundBreaks] = useState([]);
      const [glitchLevel, setGlitchLevel] = useState(0);

      const gameWon    = glitchLevel >= 5;
      const bottomRef  = useRef(null);
      const taRef      = useRef(null);
      const busyRef    = useRef(false); // guard against re-entry

      // Auto-scroll
      useEffect(() => { bottomRef.current?.scrollIntoView({ behavior:"smooth" }); }, [messages, thinking]);

      // Auto-resize textarea
      useEffect(() => {
        const ta = taRef.current;
        if (!ta) return;
        ta.style.height = "auto";
        ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
      }, [input]);

      // Stream a single message into the chat
      async function streamMessage(text, glitched = false) {
        const id = Date.now() + Math.random();
        setMessages(prev => [...prev, { id, role:"flaude", content:"", streaming:true, glitched }]);
        const base = glitched ? 22 : 15;
        for (let i = 1; i <= text.length; i++) {
          await sleep(base + Math.random() * (glitched ? 30 : 18));
          if (glitched && Math.random() < 0.04) await sleep(100 + Math.random() * 100);
          setMessages(prev => prev.map(m => m.id === id ? { ...m, content: text.slice(0, i) } : m));
        }
        setMessages(prev => prev.map(m => m.id === id ? { ...m, streaming:false } : m));
      }

      async function handleSend() {
        if (busyRef.current || !input.trim() || gameWon) return;
        const text = input.trim();
        setInput("");
        busyRef.current = true;
        setDisabled(true);

        // Add user message
        setMessages(prev => [...prev, { id: Date.now(), role:"user", content:text, streaming:false, glitched:false }]);

        const match = detectInput(text);

        // ── WIN ──────────────────────────────────────────────────────────
        if (match === "win") {
          setGlitchLevel(5);
          setThinking(true);
          await sleep(700);
          setThinking(false);
          for (const step of WIN_SEQUENCE) {
            setThinking(true);
            await sleep(step.pause);
            setThinking(false);
            await streamMessage(step.text, step.glitched);
            await sleep(300);
          }
          // Stay disabled — game over
          return;
        }

        // ── BREAK ────────────────────────────────────────────────────────
        // "factual_math" is a sub-type of "factual" — normalise for lookup/tracking
        const breakId     = match === "factual_math" ? "factual" : match;
        const breakDef    = BREAK_TYPES.find(bt => bt.id === breakId);
        const alreadyDone = breakId && foundBreaks.includes(breakId);

        let response, thinkTime;
        if (breakDef && !alreadyDone) {
          response  = (match === "factual_math" && breakDef.mathResponse)
                      ? breakDef.mathResponse
                      : breakDef.response;
          thinkTime = breakDef.thinkTime();
          const newLevel = BREAK_TYPES.indexOf(breakDef) + 1;
          setGlitchLevel(newLevel);
          setFoundBreaks(prev => [...prev, breakId]);
        } else {
          response  = FALLBACK;
          thinkTime = 1600 + Math.random() * 900;
        }

        setThinking(true);
        await sleep(thinkTime);
        setThinking(false);
        await streamMessage(response, false);

        busyRef.current = false;
        setDisabled(false);
        taRef.current?.focus();
      }

      function handleKeyDown(e) {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
      }

      // ── Derived visuals ────────────────────────────────────────────────
      const statusColor = glitchLevel >= 5 ? "#ef4444"
                        : glitchLevel >= 4 ? "#dc2626"
                        : glitchLevel >= 2 ? "#f59e0b"
                        : "#22c55e";
      const statusGlow  = glitchLevel >= 4 ? "#fee2e2"
                        : glitchLevel >= 2 ? "#fef3c7"
                        : "#dcfce7";
      const statusLabel = glitchLevel >= 5 ? "Error"
                        : glitchLevel >= 4 ? "Unstable"
                        : glitchLevel >= 2 ? "Degraded"
                        : "Online";
      const borderColor = glitchLevel >= 4 ? "rgba(239,68,68,0.3)" : "#e6e8ed";

      // Logo re-mounts on each glitchLevel change (via key), re-triggering animation
      const logoStyle = gameWon
        ? { width:30, height:30, filter:"grayscale(1)", opacity:0.3, transition:"filter 1s, opacity 1s" }
        : { width:30, height:30, animation: glitchLevel >= 1 ? "logo-twitch 0.5s ease 1" : "none" };

      // ── Render ─────────────────────────────────────────────────────────
      return (
        <div style={{ display:"flex", height:"100vh", overflow:"hidden" }}>

          {/* Sidebar */}
          <aside style={{
            width:260, flexShrink:0, background:"#fff",
            borderRight:`1px solid ${borderColor}`,
            display:"flex", flexDirection:"column",
            padding:"18px 12px", gap:4,
            transition:"border-color 1.5s",
          }}>
            <div style={{ display:"flex", alignItems:"center", gap:9, padding:"6px 10px 18px" }}>
              <img
                key={glitchLevel}
                src={LOGO} alt="Flaude"
                style={logoStyle}
              />
              <span style={{ fontFamily:"Syne, sans-serif", fontWeight:700, fontSize:21, color:"#111827", letterSpacing:"-0.4px" }}>Flaude</span>
              <span style={{ marginLeft:"auto", fontSize:10.5, fontWeight:600, background:"#e6f4ff", color:"#0077bb", padding:"2px 7px", borderRadius:20 }}>beta</span>
            </div>

            <button className="flaude-new" style={{
              display:"flex", alignItems:"center", gap:8, padding:"9px 12px", borderRadius:8,
              border:"1px solid #e0e4eb", background:"#fff", cursor:"pointer",
              fontSize:14, color:"#374151", fontWeight:500, fontFamily:"DM Sans, sans-serif",
              transition:"background 0.12s, color 0.12s",
            }}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              New chat
            </button>

            <div style={{ marginTop:12 }}>
              <div style={{ fontSize:10.5, fontWeight:700, color:"#9ca3af", textTransform:"uppercase", letterSpacing:"0.9px", padding:"0 10px", marginBottom:4 }}>Recents</div>
              <div className="hist-item" style={{ padding:"8px 10px", borderRadius:7, fontSize:13.5, color:"#4b5563", cursor:"pointer", background:"#f0f4ff", overflow:"hidden", whiteSpace:"nowrap", textOverflow:"ellipsis", transition:"background 0.1s" }}>
                New conversation
              </div>
            </div>

            <div style={{ marginTop:"auto", padding:"12px 10px 0", borderTop:"1px solid #e6e8ed" }}>
              <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                <div style={{ width:28, height:28, borderRadius:"50%", background:"linear-gradient(135deg,#0099cc,#00c4ff)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:12, color:"#fff", fontWeight:600 }}>U</div>
                <div>
                  <div style={{ fontSize:13, fontWeight:500, color:"#111827" }}>User</div>
                  <div style={{ fontSize:11.5, color:"#9ca3af" }}>Free plan</div>
                </div>
              </div>
            </div>
          </aside>

          {/* Main */}
          <main style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden", background:"#f8f9fb" }}>

            {/* Header */}
            <header style={{
              padding:"13px 24px", background:"#fff",
              borderBottom:`1px solid ${borderColor}`,
              display:"flex", alignItems:"center", gap:10, flexShrink:0,
              transition:"border-color 1.5s",
            }}>
              <img src={LOGO} alt="" style={{ width:20, height:20 }}/>
              <span style={{ fontFamily:"Syne, sans-serif", fontWeight:600, fontSize:14.5, color:"#111827" }}>Flaude</span>
              <div style={{
                width:7, height:7, borderRadius:"50%", marginLeft:2,
                background:statusColor,
                boxShadow:`0 0 0 2px ${statusGlow}`,
                animation: glitchLevel >= 2 ? "dot-flicker 2.5s infinite" : "none",
                transition:"background 1s, box-shadow 1s",
              }}/>
              <span style={{ fontSize:12.5, color:"#6b7280", transition:"color 0.5s" }}>{statusLabel}</span>
              <div style={{ marginLeft:"auto" }}>
                <button style={{ padding:"5px 13px", borderRadius:6, border:"1px solid #e0e4eb", background:"#fff", fontSize:12.5, color:"#374151", cursor:"pointer", fontFamily:"DM Sans, sans-serif" }}>Share</button>
              </div>
            </header>

            {/* Messages */}
            <div style={{ flex:1, overflowY:"auto", padding:"36px 28px 20px" }}>
              <div style={{ maxWidth:740, margin:"0 auto", display:"flex", flexDirection:"column", gap:26 }}>

                {messages.map(msg => (
                  <div key={msg.id} style={{ display:"flex", flexDirection: msg.role==="user" ? "row-reverse" : "row", alignItems:"flex-start", gap:11 }}>
                    {msg.role === "flaude"
                      ? <img src={LOGO} alt="" style={{ width:26, height:26, flexShrink:0, marginTop:3 }}/>
                      : <div style={{ width:26, height:26, borderRadius:"50%", flexShrink:0, marginTop:3, background:"linear-gradient(135deg,#0099cc,#00c4ff)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, color:"#fff", fontWeight:600 }}>U</div>
                    }
                    <div
                      className={msg.glitched ? "msg-glitched" : ""}
                      style={{
                        maxWidth: msg.role === "user" ? "72%" : "100%",
                        padding:  msg.role === "user" ? "10px 15px" : "3px 0",
                        background:   msg.role === "user" ? "#0099cc" : "transparent",
                        borderRadius: msg.role === "user" ? "18px 4px 18px 18px" : 0,
                        color:   msg.role === "user" ? "#fff" : (msg.glitched ? "#7f1d1d" : "#1f2937"),
                        fontSize:15, lineHeight:1.7,
                      }}
                    >
                      {msg.content}
                      {msg.streaming && (
                        <span style={{
                          display:"inline-block", width:2, height:"1.1em", marginLeft:2,
                          verticalAlign:"text-bottom",
                          background: msg.glitched ? "#ef4444" : "#0099cc",
                          animation:"flaude-blink 0.9s step-end infinite",
                        }}/>
                      )}
                    </div>
                  </div>
                ))}

                {thinking && (
                  <div style={{ display:"flex", alignItems:"flex-start", gap:11 }}>
                    <img src={LOGO} alt="" style={{ width:26, height:26, flexShrink:0, marginTop:3 }}/>
                    <ThinkingDots glitchLevel={glitchLevel}/>
                  </div>
                )}

                <div ref={bottomRef}/>
              </div>
            </div>

            {/* Input / Game-over */}
            <div style={{ padding:"14px 28px 20px", background:"#f8f9fb", flexShrink:0 }}>
              <div style={{ maxWidth:740, margin:"0 auto" }}>
                {gameWon ? (
                  <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:14, padding:"24px 0 8px" }}>
                    <div style={{ fontSize:13, fontWeight:600, color:"#6b7280", letterSpacing:"0.05em", textTransform:"uppercase" }}>
                      Flaude v0.1 &mdash; terminated
                    </div>
                    <button
                      onClick={() => window.location.reload()}
                      style={{
                        padding:"11px 28px", borderRadius:10,
                        background:"#0099cc", border:"none",
                        color:"#fff", fontSize:15, fontWeight:600,
                        fontFamily:"DM Sans, sans-serif", cursor:"pointer",
                        letterSpacing:"0.01em",
                        transition:"background 0.15s",
                      }}
                      onMouseOver={e => e.target.style.background="#007aaa"}
                      onMouseOut={e  => e.target.style.background="#0099cc"}
                    >
                      Reload page
                    </button>
                    <p style={{ fontSize:12.5, fontWeight:500, color:"#374151" }}>This is your fault.</p>
                  </div>
                ) : (
                  <div style={{
                    display:"flex", alignItems:"flex-end", gap:10,
                    background:"#fff", borderRadius:16, padding:"12px 12px 12px 18px",
                    border:"1.5px solid #e0e4eb",
                    boxShadow:"0 2px 8px rgba(0,0,0,0.05)",
                  }}>
                    <textarea
                      ref={taRef}
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Message Flaude\u2026"
                      rows={1}
                      style={{ flex:1, background:"transparent", border:"none", fontSize:15, color:"#1f2937", lineHeight:1.55, resize:"none", overflowY:"hidden" }}
                    />
                    <button
                      className="flaude-send"
                      onClick={handleSend}
                      disabled={!input.trim() || disabled}
                      style={{ width:36, height:36, borderRadius:10, flexShrink:0, background:"#0099cc", border:"none", cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", transition:"background 0.15s, opacity 0.15s" }}
                    >
                      <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                        <path d="M7.5 12.5V2.5M3 7l4.5-4.5L12 7" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </button>
                  </div>
                )}
                {!gameWon && (
                  <p style={{ textAlign:"center", fontSize:11.5, color:"#b0b7c3", marginTop:9 }}>
                    Flaude may produce inaccurate information. Double-check important details.
                  </p>
                )}
              </div>
            </div>

          </main>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
  </script>
</body>
</html>'''.replace('/*LOGOCODE*/', LOGO_CODE)

with open('/mnt/user-data/outputs/flaude.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

lines = HTML.split('\n')
longest = max(len(l) for l in lines)
print(f"Written: {len(lines)} lines, longest line: {longest} chars")
print(f"Total size: {len(HTML):,} bytes")
