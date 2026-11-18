// テスト画面の「挙動」＝送信・計測・表示（構造は index.html・見た目は style.css）
// やること: AIボタンが押されたら、指定件数を並列でゲートウェイへ送り、
// 送信時刻／最後の応答の受信時刻／全体所要時間と、各リクエストの結果を表示する。
// 利用者ID・仮想キーは、入力があるときだけ封筒（JSON）に載せてゲートウェイへ渡す。

// 時刻を HH:MM:SS.mmm の形に整える
const fmtTime = (d) =>
  d.toLocaleTimeString("ja-JP", { hour12: false }) +
  "." + String(d.getMilliseconds()).padStart(3, "0");

// 1リクエストを送り、状態・個別所要時間・本文を返す（失敗もここで受け止める）
const sendOne = async (i, payload) => {
  const started = performance.now();
  try {
    const res = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json();
    return { i: i, label: "HTTP " + res.status, ms: performance.now() - started, body: body };
  } catch (e) {
    return { i: i, label: "fetch失敗", ms: performance.now() - started, body: String(e) };
  }
};

document.getElementById("send").onclick = async () => {
  const out = document.getElementById("out");
  const n = Math.max(1, parseInt(document.getElementById("conc").value, 10) || 1);

  // 封筒を組み立てる（利用者ID・仮想キーは入力があるときだけ載せる）
  const payload = { message: document.getElementById("msg").value };
  const user = document.getElementById("user").value.trim();
  const vkey = document.getElementById("vkey").value.trim();
  if (user) payload.user = user;
  if (vkey) payload.api_key = vkey;

  // 送信時刻を記録し、前回の受信時刻・所要時間は初期化する
  document.getElementById("t-sent").textContent = fmtTime(new Date());
  document.getElementById("t-recv").textContent = "−";
  document.getElementById("t-dur").textContent = "−";
  out.textContent = "送信中…（" + n + " 件並列）";

  const t0 = performance.now();
  const results = await Promise.all(
    Array.from({ length: n }, (_, i) => sendOne(i + 1, payload))
  );

  // 全応答がそろった時刻と全体所要時間を表示する
  const total = performance.now() - t0;
  document.getElementById("t-recv").textContent = fmtTime(new Date());
  document.getElementById("t-dur").textContent =
    Math.round(total) + " ms（" + (total / 1000).toFixed(2) + " 秒）";

  const lines = results.map(
    (r) => "#" + r.i + "  " + r.label + "  " + Math.round(r.ms) + " ms"
  );
  const first = results[0];
  const firstBody =
    typeof first.body === "string" ? first.body : JSON.stringify(first.body, null, 2);
  out.textContent = lines.join("\n") + "\n\n--- #1 の応答本文 ---\n" + firstBody;
};
