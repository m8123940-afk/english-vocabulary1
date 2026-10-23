// Telegram Mini App. Данные и проверка — на сервере; здесь только интерфейс и голос.
const tg = window.Telegram && window.Telegram.WebApp;
if (tg) { tg.ready(); tg.expand(); }
const params = new URLSearchParams(location.search);
const AUTH = params.get("dev") ? "dev:" + params.get("dev") : "tma " + (tg ? tg.initData : "");
const app = document.getElementById("app");
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

async function api(method, path, body) {
  const res = await fetch("/api" + path, {
    method,
    headers: { "Content-Type": "application/json", Authorization: AUTH },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || ("Ошибка " + res.status));
  return data;
}
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sign = (n) => (n > 0 ? "+" : "") + n;
function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => (t.hidden = true), 3000);
}
const fail = (e) => toast(e.message || String(e));
const view = (html) => { app.innerHTML = html; window.scrollTo(0, 0); };
const go = (name) => { location.hash = name; };
function markTab(name) {
  document.querySelectorAll(".tabbar a").forEach((a) => a.classList.toggle("active", a.dataset.tab === name));
}

// ---------- голос ----------
let ttsRate = 1;
api("GET", "/settings").then((s) => (ttsRate = s.tts_rate)).catch(() => {});

// Произносим слово и только потом начинаем слушать ответ.
function sayThenListen(word, onDone) {
  if (!("speechSynthesis" in window)) return onDone();
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(word);
  u.lang = "en-US"; u.rate = ttsRate;
  u.onend = onDone; u.onerror = onDone;
  speechSynthesis.speak(u);
}
let recognizer = null;
function listenOnce(onResult, onError) {
  if (!SR) return onError(new Error("Голосовой ввод недоступен в этом браузере"));
  recognizer = new SR();
  recognizer.lang = "ru-RU"; recognizer.maxAlternatives = 5; recognizer.interimResults = false;
  recognizer.onresult = (e) => onResult([...e.results[0]].map((a) => a.transcript));
  recognizer.onerror = (e) => onError(new Error(e.error === "not-allowed" ? "Нет доступа к микрофону" : "Не расслышал, повторите"));
  recognizer.onnomatch = () => onError(new Error("Не расслышал, повторите"));
  recognizer.onend = () => { if (recognizer && recognizer.onfinish) recognizer.onfinish(); };
  recognizer.start();
}
function stopListening() { try { recognizer && recognizer.stop(); } catch (_) {} }

// ---------- главная ----------
async function viewHome() {
  markTab("");
  const [stats, points] = await Promise.all([api("GET", "/stats"), api("GET", "/points")]);
  const t = stats.totals;
  view(`<h1>Привет! 👋</h1><p class="sub">Учим английские слова с голосом</p>
    <div class="hero">
      <div class="label">Общий баланс</div>
      <div class="big">${sign(points.balance)} ⭐</div>
      <div class="label" style="margin-top:10px">Точность ${stats.percent}% · слов проверено ${t.total}</div>
    </div>
    <div class="grid2" style="margin-top:14px">
      <a class="tile" href="#train"><span class="ico">🎯</span>Тренировка</a>
      <a class="tile" href="#source"><span class="ico">🌐</span>Источник слов</a>
    </div>`);
}

// ---------- тренировка ----------
async function viewTrain() {
  markTab("train");
  const st = await api("GET", "/train/state");
  if (st.active) return showQuestion(st);
  const units = await api("GET", "/train/units");
  if (!units.length) {
    return view(`<h1>Тренировка</h1>
      <div class="card empty"><span class="ico">📭</span>Слов пока нет.<br>Загрузите словарь, и можно начинать.
        <a class="btn" href="#source" style="margin-top:14px">🌐 Загрузить словарь</a></div>`);
  }
  view(`<h1>Тренировка</h1><p class="sub">Выберите Unit и Part</p>` + units.map((u) => `
    <div class="card">
      <div class="row" style="margin-bottom:6px"><b style="font-size:17px">Unit ${esc(u.unit)}</b><span class="pill">${u.count} слов</span></div>
      <button class="btn" onclick="startTrain('${esc(u.unit)}','*')">▶︎ Все Part</button>
      ${u.parts.map((p) => `<button class="btn ghost" onclick="startTrain('${esc(u.unit)}','${esc(p.part)}')">
        ${p.part ? "Part " + esc(p.part) : "Без Part"} · ${p.count} слов</button>`).join("")}
    </div>`).join(""));
}
window.startTrain = async (unit, part) => { try { showQuestion(await api("POST", "/train/start", { unit, part })); } catch (e) { fail(e); } };
window.againTrain = async () => { try { showQuestion(await api("POST", "/train/again")); } catch (e) { fail(e); } };
window.retryFrom = async (sid) => { try { showQuestion(await api("POST", `/train/retry/${sid}`)); } catch (e) { fail(e); } };

let current = null; // {st, heard: [..]}
function ring(done, total) {
  const r = 62, c = 2 * Math.PI * r, pct = total ? done / total : 0;
  return `<svg class="ring" viewBox="0 0 150 150">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6366f1"/><stop offset="1" stop-color="#ec4899"/></linearGradient></defs>
    <circle class="bg" cx="75" cy="75" r="${r}" stroke-width="12" fill="none"/>
    <circle class="fg" cx="75" cy="75" r="${r}" stroke-width="12" fill="none" stroke-linecap="round"
      transform="rotate(-90 75 75)" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - pct)}"/>
    <text x="75" y="72" text-anchor="middle" class="ring-text">${done}/${total}</text>
    <text x="75" y="92" text-anchor="middle" class="ring-sub">слов</text></svg>`;
}

function showQuestion(st) {
  current = { st, heard: null };
  const title = st.mode === "retry" ? "🔁 Повтор ошибок" : `Unit ${esc(st.unit)}${st.part === "*" ? "" : " · Part " + esc(st.part)}`;
  view(`<h1>${title}</h1>
    <div class="card stage">
      ${ring(st.index, st.total)}
      <div class="sub" style="margin:0">Слово ${Math.min(st.index + 1, st.total)} из ${st.total} · ошибок: ${st.errors}</div>
      <div id="status" class="status" style="margin-top:12px">🔊 Слушайте слово…</div>
      <div class="mic-wrap">
        <button id="mic" class="mic" onclick="toggleMic()" disabled>🎤</button>
        <span class="pulse"></span><span class="pulse p2"></span>
      </div>
      <div class="heard" id="heard"><span class="lbl">Вы сказали</span><span id="heardText" class="muted">—</span></div>
      <div id="verdictBox"></div>
      <div class="actions" id="actions">
        <button class="btn" id="checkBtn" onclick="checkAnswer()" disabled>✅ Проверить</button>
        <button class="btn ghost" onclick="skipWord()">⏭ Пропустить</button>
      </div>
    </div>
    <button class="btn ghost danger" style="color:var(--bad)" onclick="finishTrain()">⏹ Завершить тренировку</button>`);
  sayThenListen(st.word_en, () => startListening());
}

function setStatus(text) { const el = document.getElementById("status"); if (el) el.textContent = text; }
function setMic(state) {
  const mic = document.getElementById("mic");
  if (!mic) return;
  mic.disabled = state === "off";
  mic.classList.toggle("listening", state === "listening");
}

function startListening() {
  if (!current || current.verdict) return;
  if (!SR) {
    setStatus("Голос недоступен в этом браузере. Нажмите «Пропустить» или откройте приложение в Telegram на телефоне.");
    return;
  }
  setMic("listening");
  setStatus("🎙 Говорите перевод…");
  listenOnce(
    (alts) => {
      setMic("idle");
      current.heard = alts;
      document.getElementById("heardText").textContent = alts[0];
      document.getElementById("heardText").className = "";
      document.getElementById("checkBtn").disabled = false;
      setStatus("Проверьте распознанное и нажмите «Проверить»");
    },
    (err) => { setMic("idle"); setStatus(err.message + " — нажмите микрофон"); }
  );
}
window.toggleMic = () => {
  if (!current) return;
  const mic = document.getElementById("mic");
  if (mic.classList.contains("listening")) { stopListening(); setMic("idle"); setStatus("Нажмите микрофон, чтобы говорить"); }
  else startListening();
};

window.checkAnswer = async () => {
  if (!current || !current.heard) return;
  const btn = document.getElementById("checkBtn");
  btn.disabled = true;
  try {
    const r = await api("POST", "/train/answer", { said: current.heard[0], alternatives: current.heard.slice(1) });
    showVerdict(r);
  } catch (e) { btn.disabled = false; fail(e); }
};
window.skipWord = async () => {
  try { showVerdict(await api("POST", "/train/skip")); } catch (e) { fail(e); }
};

function showVerdict(r) {
  current.verdict = true;
  setMic("off");
  stopListening();
  setStatus("");
  const ok = !!r.correct;
  document.getElementById("verdictBox").innerHTML = `
    <div class="verdict ${ok ? "ok" : "bad"}">
      <div class="head">${ok ? "🎉 Верно!" : r.skipped ? "⏭ Пропущено" : "❌ Не совсем"}</div>
      <div class="tr">${esc(r.ru)}</div>
      <div class="en">${esc(r.en)}${r.said && !r.skipped ? " · вы сказали: «" + esc(r.said) + "»" : ""}</div>
    </div>`;
  document.getElementById("actions").innerHTML = `<button class="btn" style="grid-column:1/-1" onclick="nextStep()">${r.done >= r.total ? "🏁 Итоги тренировки" : "Дальше →"}</button>`;
  current.progress = { done: r.done, total: r.total, errors: r.errors };
}
window.nextStep = async () => {
  try {
    const st = await api("GET", "/train/state");
    if (!st.active || st.word_en === null) return finishTrain();
    showQuestion(st);
  } catch (e) { fail(e); }
};
window.finishTrain = async () => {
  try {
    const rep = await api("POST", "/train/finish");
    const pct = rep.percent;
    view(`<h1>🏁 Готово!</h1>
      <div class="hero" style="text-align:center">
        <div class="label">Точность</div><div class="big">${pct}%</div>
        <div class="label" style="margin-top:6px">${rep.mode === "retry" ? "Повтор без начисления баллов" : "Баллы за тренировку: " + sign(rep.points)}</div>
      </div>
      <div class="grid2" style="margin-top:12px">
        <div class="card" style="text-align:center"><div class="sub" style="margin:0">Правильно</div><b style="font-size:24px">${rep.correct}</b></div>
        <div class="card" style="text-align:center"><div class="sub" style="margin:0">Ошибок</div><b style="font-size:24px">${rep.errors}</b></div>
        <div class="card" style="text-align:center"><div class="sub" style="margin:0">Пропусков</div><b style="font-size:24px">${rep.skipped}</b></div>
        <div class="card" style="text-align:center"><div class="sub" style="margin:0">Баланс</div><b style="font-size:24px">${rep.balance}</b></div>
      </div>
      ${rep.wrong_ids.length ? `<button class="btn" onclick="retryFrom(${rep.session_id})">🔁 Повторить ошибки (${rep.wrong_ids.length})</button>` : ""}
      <button class="btn ghost" onclick="againTrain()">🔄 Пройти заново</button>
      <button class="btn ghost" onclick="go('home')">🏠 На главную</button>`);
    current = null;
  } catch (e) { fail(e); }
};

// ---------- слова ----------
async function viewWords() {
  markTab("words");
  const words = await api("GET", "/words");
  view(`<h1>Мои слова <span class="pill">${words.length}</span></h1>
    <div class="card">
      <h2 style="margin-top:0">Добавить слово</h2>
      <input id="w-en" placeholder="English, например: apple">
      <input id="w-ru" placeholder="Перевод, например: яблоко">
      <button class="btn" onclick="addWord()">➕ Добавить</button>
    </div>
    <div class="card">${words.slice(0, 300).map((w) => `
      <div class="li"><div><b>${esc(w.en)}</b> — ${esc(w.ru)}<small>Unit ${esc(w.unit)}${w.part ? " · Part " + esc(w.part) : ""}</small></div>
        <div class="row auto"><button class="btn ghost small" onclick="editWord(${w.id},'${esc(w.en)}','${esc(w.ru)}')">✏️</button>
        <button class="btn danger small" onclick="delWord(${w.id})">🗑</button></div></div>`).join("") ||
      `<div class="empty"><span class="ico">📭</span>Список пуст</div>`}
    </div>`);
}
window.addWord = async () => {
  const en = document.getElementById("w-en").value.trim(), ru = document.getElementById("w-ru").value.trim();
  try { await api("POST", "/words", { en, ru }); toast("Слово добавлено ✨"); viewWords(); } catch (e) { fail(e); }
};
window.editWord = async (id, en, ru) => {
  const newEn = prompt("Английское слово", en); if (newEn === null) return;
  const newRu = prompt("Перевод", ru); if (newRu === null) return;
  try { await api("PUT", `/words/${id}`, { en: newEn, ru: newRu }); viewWords(); } catch (e) { fail(e); }
};
window.delWord = async (id) => {
  if (!confirm("Удалить слово?")) return;
  try { await api("DELETE", `/words/${id}`); viewWords(); } catch (e) { fail(e); }
};

// ---------- статистика ----------
async function viewStats() {
  markTab("stats");
  const s = await api("GET", "/stats");
  const t = s.totals;
  view(`<h1>Статистика</h1>
    <div class="hero"><div class="label">Процент правильных</div><div class="big">${s.percent}%</div>
      <div class="label" style="margin-top:6px">Баланс: ${sign(s.balance)} ⭐</div></div>
    <div class="card" style="margin-top:14px">
      <div class="stat"><span>Всего слов</span><b>${t.total}</b></div>
      <div class="stat"><span>✅ Правильных</span><b>${t.correct}</b></div>
      <div class="stat"><span>❌ Ошибок</span><b>${t.errors}</b></div>
      <div class="stat"><span>⏭ Пропусков</span><b>${t.skipped}</b></div>
    </div>
    <h2>По Unit и Part</h2>
    <div class="card">${s.by_unit_part.map((r) => `<div class="stat"><span>Unit ${esc(r.unit)} · Part ${esc(r.part || "—")}</span>
      <b>${r.total ? Math.round(100 * r.correct / r.total) : 0}% · ${r.total}</b></div>`).join("") || `<div class="empty">Данных пока нет</div>`}</div>
    <h2>История</h2>
    <div class="card">${s.history.map((h) => `<div class="stat"><span>Unit ${esc(h.unit)} ${esc(h.part)}${h.mode === "retry" ? " · повтор" : ""}</span>
      <b class="pts ${h.points >= 0 ? "pos" : "neg"}">${sign(h.points)}</b></div>`).join("") || `<div class="empty">Тренировок пока нет</div>`}</div>`);
}

// ---------- баллы ----------
async function viewPoints() {
  markTab("points");
  const p = await api("GET", "/points");
  view(`<h1>Мои баллы</h1>
    <div class="hero" style="text-align:center"><div class="label">Общий баланс</div><div class="big">${sign(p.balance)} ⭐</div></div>
    <h2>Последние тренировки</h2>
    <div class="card">${p.history.map((h) => `<div class="stat"><span>Unit ${esc(h.unit)} ${esc(h.part)}</span>
      <b class="pts ${h.points >= 0 ? "pos" : "neg"}">${sign(h.points)}</b></div>`).join("") || `<div class="empty">Пока нет тренировок</div>`}</div>
    <a class="btn ghost" href="#settings">📋 Таблица баллов</a>`);
}

// ---------- ещё: настройки, таблица баллов, источник ----------
async function viewSettings() {
  markTab("settings");
  const [s, rules] = await Promise.all([api("GET", "/settings"), api("GET", "/rules")]);
  view(`<h1>Настройки</h1>
    <div class="card">
      <h2 style="margin-top:0">Тренировка</h2>
      <label class="sub" style="margin:6px 0 0">Слов за тренировку</label>
      <select id="s-words">${[5, 10, 15, 20, 30].map((n) => `<option ${n === s.words_per_session ? "selected" : ""}>${n}</option>`).join("")}</select>
      <label class="sub" style="margin:6px 0 0">Скорость произношения</label>
      <select id="s-rate"><option value="0.7" ${s.tts_rate < 0.9 ? "selected" : ""}>Медленная</option><option value="1" ${s.tts_rate >= 0.9 ? "selected" : ""}>Обычная</option></select>
      <label class="check"><input type="checkbox" id="s-shuffle" ${s.shuffle ? "checked" : ""}> Случайный порядок</label>
      <label class="check"><input type="checkbox" id="s-retry" ${s.retry_errors ? "checked" : ""}> Повторять ошибки после тренировки</label>
      <button class="btn" onclick="saveSettings()">Сохранить</button>
    </div>
    <div class="card">
      <h2 style="margin-top:0">Таблица баллов</h2>
      ${rules.overlaps ? `<p class="sub">⚠️ Есть пересекающиеся диапазоны — применяется первое подходящее.</p>` : ""}
      ${rules.rules.map((r) => `<div class="li"><div>${ruleLabel(r)}</div>
        <div class="row auto"><button class="btn ghost small" onclick="editRule(${r.id})">✏️</button>
        <button class="btn danger small" onclick="delRule(${r.id})">🗑</button></div></div>`).join("")}
      <h2>Новое правило</h2>
      <div class="row"><input id="r-min" type="number" min="0" placeholder="от ошибок"><input id="r-max" type="number" min="0" placeholder="до (пусто = ∞)"></div>
      <select id="r-pts">${pointOptions(0)}</select>
      <button class="btn" onclick="addRule()">➕ Добавить правило</button>
      <button class="btn ghost" onclick="resetRules()">♻️ Стандартная таблица</button>
    </div>
    <div class="card">
      <h2 style="margin-top:0">Источник слов</h2>
      <a class="btn" href="#source">🌐 Загрузить слова</a>
    </div>`);
}
const ruleLabel = (r) => {
  const rng = r.max_errors === null ? `${r.min_errors}+` : r.min_errors === r.max_errors ? `${r.min_errors}` : `${r.min_errors}–${r.max_errors}`;
  return `<b>${rng}</b> ошибок → <b class="pts ${r.points >= 0 ? "pos" : "neg"}">${sign(r.points)}</b> баллов`;
};
const pointOptions = (sel) => [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5].map((v) => `<option value="${v}" ${v === sel ? "selected" : ""}>${sign(v)}</option>`).join("");
window.saveSettings = async () => {
  try {
    await api("PUT", "/settings", {
      words_per_session: Number(document.getElementById("s-words").value),
      tts_rate: Number(document.getElementById("s-rate").value),
      shuffle: document.getElementById("s-shuffle").checked,
      retry_errors: document.getElementById("s-retry").checked,
    });
    toast("Сохранено ✅"); viewSettings();
  } catch (e) { fail(e); }
};
window.addRule = async () => {
  const maxRaw = document.getElementById("r-max").value.trim();
  try {
    await api("POST", "/rules", { min_errors: Number(document.getElementById("r-min").value), max_errors: maxRaw === "" ? null : Number(maxRaw), points: Number(document.getElementById("r-pts").value) });
    toast("Правило добавлено"); viewSettings();
  } catch (e) { fail(e); }
};
window.editRule = async (id) => {
  const { rules } = await api("GET", "/rules");
  const r = rules.find((x) => x.id === id);
  const min = prompt("От ошибок", r.min_errors); if (min === null) return;
  const max = prompt("До ошибок (пусто = ∞)", r.max_errors ?? ""); if (max === null) return;
  const pts = prompt("Баллы (от -5 до 5)", r.points); if (pts === null) return;
  try {
    await api("PUT", `/rules/${id}`, { min_errors: Number(min), max_errors: max.trim() === "" ? null : Number(max), points: Number(pts) });
    viewSettings();
  } catch (e) { fail(e); }
};
window.delRule = async (id) => {
  if (!confirm("Удалить правило?")) return;
  try { await api("DELETE", `/rules/${id}`); viewSettings(); } catch (e) { fail(e); }
};
window.resetRules = async () => {
  if (!confirm("Вернуть стандартную таблицу баллов?")) return;
  try { await api("POST", "/rules/reset"); toast("Стандартная таблица восстановлена"); viewSettings(); } catch (e) { fail(e); }
};

function viewSource() {
  markTab("settings");
  view(`<h1>Источник слов</h1>
    <div class="card"><h2 style="margin-top:0">📘 Встроенный словарь</h2>
      <p class="sub">Navigate B1+, Unit 1–12, 800 слов с переводами</p>
      <button class="btn" onclick="loadBundled()">Загрузить</button></div>
    <div class="card"><h2 style="margin-top:0">🔗 Ссылка на сайт</h2>
      <input id="src-url" placeholder="https://...">
      <button class="btn" onclick="loadUrl()">Загрузить по ссылке</button></div>
    <div class="card"><h2 style="margin-top:0">✍️ Вручную</h2>
      <textarea id="src-text" placeholder="apple - яблоко&#10;cat - кот"></textarea>
      <button class="btn" onclick="loadManual()">Добавить в «Мои»</button></div>`);
}
window.loadBundled = async () => { try { const r = await api("POST", "/source/bundled"); toast(`Загружено: ${r.loaded}, новых ${r.added}`); go("train"); } catch (e) { fail(e); } };
window.loadUrl = async () => { try { const r = await api("POST", "/source/url", { url: document.getElementById("src-url").value.trim() }); toast(`Загружено слов: ${r.loaded}`); go("train"); } catch (e) { fail(e); } };
window.loadManual = async () => {
  try { const r = await api("POST", "/source/manual", { text: document.getElementById("src-text").value });
    toast(`Добавлено: ${r.added}` + (r.bad.length ? `, не распознано: ${r.bad.length}` : "")); } catch (e) { fail(e); }
};

// ---------- маршрутизация ----------
const ROUTES = { home: viewHome, train: viewTrain, words: viewWords, stats: viewStats, points: viewPoints, settings: viewSettings, source: viewSource };
async function route() {
  const name = (location.hash || "#train").slice(1);
  const handler = ROUTES[name] || viewTrain;
  try { await handler(); }
  catch (e) { fail(e); view(`<div class="card empty"><span class="ico">⚠️</span>Не удалось загрузить раздел</div>`); }
}
window.go = go;
window.addEventListener("hashchange", route);
route();
