# ============================================================
# Cocoa Mascot (Web prototype, single file)
# 画面の下を歩くWeb版デスクトップマスコットの試作。
# タップでセリフ（cocobuttonと共通の24種）、ドラッグで移動、
# 時間帯で挨拶が変わる。歩行／停止／おすわり付き。
# ============================================================

# =========================
# [S1] DESIGN
# =========================
HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ UI.app_title }}</title>
<style>
*{box-sizing:border-box;}
body{margin:0;font-family:sans-serif;color:#2b1c14;background:#f7ead9;}
header{padding:14px 16px 6px;text-align:center;}
h1{margin:0;font-size:1.45rem;}
header p{margin:6px 0 0;color:#6b5546;font-size:.95rem;}
#stage{position:relative;height:62vh;min-height:380px;margin:12px;border-radius:18px;overflow:hidden;
 background:linear-gradient(#ffe9c9 0 68%,#e8c39a 68% 100%);box-shadow:inset 0 0 0 2px #d9b98c;}
.window{position:absolute;top:26px;left:26px;width:120px;height:140px;border-radius:10px;background:#bfe3f2;border:6px solid #fff7ea;}
.plant{position:absolute;right:30px;bottom:32%;font-size:52px;}
.books{position:absolute;left:30px;bottom:32%;font-size:40px;}
.floor-line{position:absolute;left:0;right:0;bottom:32%;height:2px;background:#d9b98c;}
#mascot{position:absolute;bottom:12px;left:40px;width:112px;cursor:grab;touch-action:none;user-select:none;-webkit-user-select:none;}
#mascot.dragging{cursor:grabbing;}
#mascotInner{transition:transform .18s;}
#mascot.facing-left #mascotInner{transform:scaleX(-1);}
#charImg{display:block;width:100%;pointer-events:none;filter:drop-shadow(0 4px 5px rgba(90,55,25,.35));}
#mascot.walking #charBody{animation:bob .34s infinite alternate ease-in-out;transform-origin:50% 100%;}
#mascot.jumping #charBody{animation:jump .38s ease-out;}
#mascot.sitting #charBody{transform:translateY(14px) scale(.97);}
@keyframes bob{from{transform:translateY(0) rotate(-1.7deg)}to{transform:translateY(-7px) rotate(1.7deg)}}
@keyframes jump{0%{transform:translateY(0)}45%{transform:translateY(-26px)}100%{transform:translateY(0)}}
#bubble{position:absolute;left:50%;bottom:calc(100% + 10px);transform:translateX(-50%);width:max-content;max-width:230px;
 background:#fff;color:#2b1c14;border-radius:14px;padding:9px 12px;font-size:.95rem;line-height:1.45;text-align:center;
 box-shadow:0 3px 10px rgba(80,50,20,.25);opacity:0;pointer-events:none;transition:opacity .2s;white-space:pre-wrap;z-index:3;}
#bubble.show{opacity:1;}
#bubble:after{content:"";position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);border:8px solid transparent;border-top-color:#fff;border-bottom:0;}
.controls{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;padding:2px 12px 8px;}
.controls button{padding:11px 18px;font-size:1rem;border:0;border-radius:999px;background:#7a4a2b;color:#fff;cursor:pointer;}
.controls button.secondary{background:#fff;color:#7a4a2b;box-shadow:inset 0 0 0 2px #7a4a2b;}
.meta{text-align:center;color:#6b5546;padding-bottom:18px;font-size:.95rem;}
@media (max-width:560px){
 #mascot{width:94px;}
 #stage{height:58vh;}
}
</style>
</head>
<body>
<header>
<h1>{{ UI.app_title }}</h1>
<p>{{ UI.lead }}</p>
</header>

<div id="stage">
  <div class="window"></div><div class="plant">🪴</div><div class="books">📚</div><div class="floor-line"></div>
  <div id="mascot" class="walking" role="button" aria-label="ココア" title="タップで呼ぶ／ドラッグで移動">
    <div id="bubble"></div>
    <div id="mascotInner">
    <div id="charBody"><img id="charImg" src="/cocoa.png" alt="ココア"></div>
    </div>
  </div>
</div>

<div class="controls">
  <button id="callBtn">ココアを呼ぶ</button>
  <button id="walkBtn" class="secondary">散歩を止める</button>
  <button id="sitBtn" class="secondary">おすわり</button>
</div>
<p class="meta">{{ UI.count_label }}：<span id="totalCount">{{ total }}</span>（{{ UI.today_label }}：<span id="todayCount">{{ today }}</span>）<br>
ドラッグで好きな場所へ動かせます。タップ／クリックでも反応します。</p>

<script>
const lines=[
"あなた、ちゃんと書いてる？",
"今日は少し静かですね。",
"その一言、大事にして。",
"無理しなくていいんですよ。",
"私は見ています。",
"……ふふ、呼びました？",
"おかえりなさい。待っていましたよ。",
"たまには休憩も大事です。",
"今日の言葉、あとで読み返すのが楽しみです。",
"無理に長く書かなくていいんです。短くても、あなたの言葉です。",
"ココアでも淹れましょうか。……気持ちだけですけど。",
"書く手が止まったら、深呼吸をひとつ。",
"その調子です。少しずつで大丈夫。",
"わたしはここにいますよ。",
"今日はどんな一日でした？",
"うまく書けない日もあります。それも記録のうちです。",
"あなたの言葉は、ちゃんと届いています。",
"静かな時間も、悪くないでしょう。",
"ふふ、また呼ばれましたね。",
"続き、気になります。",
"今日の一言が、明日のあなたを助けるかもしれません。",
"肩の力を抜いて。……はい、上手です。",
"書いてくれて、ありがとう。",
"夜更かしはほどほどに、ですよ。"
];
const stage=document.getElementById("stage");
const mascot=document.getElementById("mascot");
const bubble=document.getElementById("bubble");
let lastLine=-1, bubbleTimer=null;
function say(text){
  bubble.textContent=text; bubble.classList.add("show");
  clearTimeout(bubbleTimer); bubbleTimer=setTimeout(()=>bubble.classList.remove("show"),4200);
}
function randomLine(){
  let i; do{i=Math.floor(Math.random()*lines.length);}while(lines.length>1&&i===lastLine);
  lastLine=i; return lines[i];
}
function greet(){
  const h=new Date().getHours();
  if(h>=5&&h<11) return "おはようございます。今日も少しずついきましょう。";
  if(h>=11&&h<17) return "こんにちは。わたし、ここを散歩してます。";
  if(h>=17&&h<22) return "こんばんは。今日はどんな一日でした？";
  return "夜更かしはほどほどに、ですよ。";
}
// walking state
let x=40, dir=1, speed=55, walking=true, paused=false, sitting=false;
let lastTs=null, idleTimer=0, nextIdle=5;
function groundBottom(){ return 12; }
function step(ts){
  if(lastTs===null) lastTs=ts;
  const dt=Math.min((ts-lastTs)/1000,.05); lastTs=ts;
  if(walking&&!paused&&!sitting&&!drag){
    x+=dir*speed*dt;
    const maxX=stage.clientWidth-mascot.clientWidth-8;
    if(x>=maxX){x=maxX;dir=-1;}
    if(x<=8){x=8;dir=1;}
    mascot.style.left=x+"px";
    mascot.classList.toggle("facing-left",dir<0);
    mascot.classList.add("walking");
    idleTimer+=dt;
    if(idleTimer>=nextIdle){ idleTimer=0; nextIdle=4+Math.random()*6; pauseWalk(1400+Math.random()*1800); }
  }
  requestAnimationFrame(step);
}
function pauseWalk(ms){
  paused=true; mascot.classList.remove("walking");
  setTimeout(()=>{paused=false;},ms);
}
requestAnimationFrame(step);
// tap / call
function callCocoa(){
  say(randomLine());
  mascot.classList.remove("jumping"); void mascot.offsetWidth; mascot.classList.add("jumping");
  fetch("/count",{method:"POST"}).then(r=>r.json()).then(d=>{
    document.getElementById("totalCount").textContent=d.total;
    document.getElementById("todayCount").textContent=d.today;
  }).catch(()=>{});
}
document.getElementById("callBtn").addEventListener("click",callCocoa);
// walk toggle
const walkBtn=document.getElementById("walkBtn");
walkBtn.addEventListener("click",()=>{
  walking=!walking;
  mascot.classList.toggle("walking",walking);
  walkBtn.textContent=walking?"散歩を止める":"散歩をはじめる";
  if(walking) say("散歩、再開です。"); else say("ここで休憩しますね。");
});
// sit
document.getElementById("sitBtn").addEventListener("click",()=>{
  sitting=true; mascot.classList.add("sitting"); mascot.classList.remove("walking"); say("おすわり。……えらい？");
  setTimeout(()=>{sitting=false;mascot.classList.remove("sitting");},3200);
});
// drag (pointer events: PC + smartphone)
let drag=null, dragMoved=false, downAt=0;
mascot.addEventListener("pointerdown",e=>{
  drag={dx:e.clientX-mascot.getBoundingClientRect().left, dy:e.clientY-mascot.getBoundingClientRect().top};
  dragMoved=false; downAt=Date.now(); mascot.classList.add("dragging"); mascot.setPointerCapture(e.pointerId);
});
mascot.addEventListener("pointermove",e=>{
  if(!drag) return;
  const sr=stage.getBoundingClientRect();
  let nx=e.clientX-sr.left-drag.dx;
  let ny=e.clientY-sr.top-drag.dy;
  if(Math.abs(nx-x)>4) dragMoved=true;
  nx=Math.max(0,Math.min(nx,sr.width-mascot.clientWidth));
  ny=Math.max(0,Math.min(ny,sr.height-mascot.clientHeight));
  x=nx; mascot.style.left=nx+"px"; mascot.style.bottom=(sr.height-ny-mascot.clientHeight)+"px";
});
mascot.addEventListener("pointerup",e=>{
  if(!drag) return;
  const wasDrag=dragMoved||(Date.now()-downAt>350);
  drag=null; mascot.classList.remove("dragging");
  mascot.style.bottom=groundBottom()+"px";
  if(!wasDrag) callCocoa(); else { say("ここに置くのね。"); pauseWalk(1200); }
});
window.addEventListener("resize",()=>{ const maxX=stage.clientWidth-mascot.clientWidth-8; if(x>maxX){x=maxX;mascot.style.left=x+"px";} });
say(greet());
</script>
</body>
</html>
"""

# =========================
# [S2] OTHER
# =========================
from flask import Flask, render_template_string, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DESKTOP_MASCOT_DB_PATH", os.path.join(BASE_DIR, "taps.db"))

UI_TEXT = {
    "app_title": "Cocoa Mascot（Web試作）",
    "lead": "画面の下を歩く、小さなココアです。",
    "count_label": "呼ばれた回数",
    "today_label": "今日",
}

@app.context_processor
def inject():
    return dict(UI=UI_TEXT)

SQL_INIT = """
CREATE TABLE IF NOT EXISTS taps(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tapped_at TEXT NOT NULL
)
"""

def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def db_init():
    with db() as c:
        c.execute(SQL_INIT)

def today_str() -> str:
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")

def db_counts():
    with db() as c:
        total = c.execute("SELECT COUNT(*) FROM taps").fetchone()[0]
        today = c.execute(
            "SELECT COUNT(*) FROM taps WHERE tapped_at LIKE ?",
            (today_str() + "%",),
        ).fetchone()[0]
    return total, today

def db_tap():
    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    with db() as c:
        c.execute("INSERT INTO taps(tapped_at) VALUES(?)", (now,))
    return db_counts()

db_init()

# =========================
# [S3] RUN
# =========================
@app.route("/")
def index():
    total, today = db_counts()
    return render_template_string(HTML, total=total, today=today)

@app.route("/count", methods=["POST"])
def count():
    total, today = db_tap()
    return jsonify({"total": total, "today": today})

@app.route("/cocoa.png")
def cocoa_png():
    return send_from_directory(BASE_DIR, "cocoa.png", mimetype="image/png")

@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
