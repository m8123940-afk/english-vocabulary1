:root {
  --bg: var(--tg-theme-bg-color, #f3f4fb);
  --text: var(--tg-theme-text-color, #1b1f2e);
  --hint: var(--tg-theme-hint-color, #7c8196);
  --card: var(--tg-theme-secondary-bg-color, #ffffff);
  --accent: #6366f1;
  --accent2: #ec4899;
  --grad: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  --ok: #16a34a; --bad: #dc2626;
  --shadow: 0 6px 24px rgba(79, 70, 229, .12);
  --radius: 22px;
}
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
html, body { margin: 0; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
body { padding: 0 0 96px; min-height: 100vh; }
main { max-width: 560px; margin: 0 auto; padding: 16px 16px 24px; }
h1 { font-size: 24px; margin: 6px 0 4px; }
h2 { font-size: 18px; margin: 18px 0 10px; }
.sub { color: var(--hint); font-size: 14px; margin: 0 0 14px; }
.hero { background: var(--grad); color: #fff; border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
.hero .big { font-size: 34px; font-weight: 800; }
.hero .label { opacity: .85; font-size: 13px; }
.card { background: var(--card); border-radius: var(--radius); padding: 16px; margin: 12px 0; box-shadow: var(--shadow); }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tile { background: var(--card); border-radius: var(--radius); padding: 18px 12px; text-align: center; text-decoration: none; color: var(--text); box-shadow: var(--shadow); font-weight: 600; }
.tile .ico { display: block; font-size: 30px; margin-bottom: 6px; }
.btn { display: block; width: 100%; border: 0; border-radius: 16px; padding: 14px 16px; font: inherit; font-size: 16px; font-weight: 600; background: var(--grad); color: #fff; cursor: pointer; box-shadow: 0 6px 16px rgba(99,102,241,.3); text-align: center; text-decoration: none; margin: 8px 0; }
.btn.ghost { background: var(--card); color: var(--text); box-shadow: none; border: 1px solid rgba(127,127,127,.25); }
.btn.danger { background: linear-gradient(135deg, #ef4444, #f97316); box-shadow: none; }
.btn.small { display: inline-block; width: auto; padding: 8px 14px; font-size: 14px; margin: 0; }
.btn:disabled { opacity: .45; box-shadow: none; }
.btn:active { transform: scale(.98); }
input, select, textarea { font: inherit; width: 100%; padding: 13px 14px; border-radius: 14px; border: 1px solid rgba(127,127,127,.25); background: var(--bg); color: var(--text); margin: 6px 0; outline: none; }
input:focus, select:focus, textarea:focus { border-color: var(--accent); }
textarea { min-height: 110px; }
label.check { display: flex; gap: 10px; align-items: center; margin: 10px 0; font-size: 15px; }
label.check input { width: 20px; height: 20px; margin: 0; }
.row { display: flex; gap: 10px; align-items: center; }
.row > * { flex: 1; }
.row > .auto { flex: 0 0 auto; }
.li { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(127,127,127,.14); }
.li:last-child { border-bottom: 0; }
.li small { color: var(--hint); display: block; }
.stat { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(127,127,127,.12); }
.stat:last-child { border-bottom: 0; }
.pill { display: inline-block; padding: 3px 10px; border-radius: 12px; background: rgba(99,102,241,.12); color: var(--accent); font-size: 13px; font-weight: 600; }
.pts { font-weight: 700; }
.pts.pos { color: var(--ok); }
.pts.neg { color: var(--bad); }

/* тренировка */
.ring { width: 150px; height: 150px; margin: 4px auto 6px; display: block; }
.ring .bg { stroke: rgba(127,127,127,.18); }
.ring .fg { stroke: url(#g); transition: stroke-dashoffset .5s ease; }
.ring-text { font-size: 26px; font-weight: 800; fill: var(--text); }
.ring-sub { font-size: 11px; fill: var(--hint); }
.stage { text-align: center; padding: 18px 12px 16px; }
.status { font-size: 15px; color: var(--hint); min-height: 22px; }
.mic-wrap { position: relative; width: 132px; height: 132px; margin: 12px auto; }
.mic { position: relative; width: 132px; height: 132px; border-radius: 50%; border: 0; background: var(--grad); color: #fff; font-size: 46px; cursor: pointer; box-shadow: 0 10px 30px rgba(99,102,241,.35); z-index: 1; }
.mic:disabled { opacity: .5; cursor: default; }
.mic.listening { animation: breathe 1.1s ease-in-out infinite; }
.pulse { position: absolute; inset: 0; border-radius: 50%; border: 3px solid var(--accent); opacity: 0; }
.mic.listening ~ .pulse { animation: pulse 1.6s ease-out infinite; }
.mic.listening ~ .pulse.p2 { animation-delay: .8s; }
@keyframes breathe { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06); } }
@keyframes pulse { from { transform: scale(1); opacity: .6; } to { transform: scale(1.5); opacity: 0; } }
.heard { margin: 12px 0 4px; padding: 14px; border-radius: 16px; background: rgba(99,102,241,.08); min-height: 56px; font-size: 18px; font-weight: 600; }
.heard .lbl { display: block; font-size: 12px; color: var(--hint); font-weight: 500; margin-bottom: 4px; }
.verdict { border-radius: var(--radius); padding: 18px; margin-top: 12px; color: #fff; text-align: center; box-shadow: var(--shadow); }
.verdict.ok { background: linear-gradient(135deg, #16a34a, #22c55e); }
.verdict.bad { background: linear-gradient(135deg, #dc2626, #f97316); }
.verdict .head { font-size: 22px; font-weight: 800; }
.verdict .tr { font-size: 17px; margin-top: 8px; }
.verdict .en { opacity: .9; font-size: 14px; }
.actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
.toast { position: fixed; left: 50%; bottom: 96px; transform: translateX(-50%); background: #111827; color: #fff; padding: 12px 18px; border-radius: 14px; font-size: 14px; z-index: 20; max-width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,.25); }

/* нижняя навигация */
.tabbar { position: fixed; left: 0; right: 0; bottom: 0; display: flex; justify-content: space-around; padding: 8px 6px calc(8px + env(safe-area-inset-bottom, 0px)); background: color-mix(in srgb, var(--card) 88%, transparent); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); box-shadow: 0 -4px 20px rgba(0,0,0,.08); z-index: 10; }
.tabbar a { flex: 1; text-align: center; font-size: 11px; color: var(--hint); text-decoration: none; padding: 4px 0; border-radius: 12px; }
.tabbar a span { display: block; font-size: 20px; margin-bottom: 2px; }
.tabbar a.active { color: var(--accent); font-weight: 700; }
.tabbar a.active span { transform: translateY(-2px); }
.empty { text-align: center; padding: 28px 12px; color: var(--hint); }
.empty .ico { font-size: 44px; display: block; margin-bottom: 8px; }
