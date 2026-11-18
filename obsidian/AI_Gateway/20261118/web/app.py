"""仮実装（スタブ）── web（Flask）の最小テスト画面。学習で本人が書き換える前提。

役割: GW開発者がテストに使う1ページを配信する。AIボタンはブラウザから
ゲートウェイ（http://localhost:8000）を直接 fetch し、リクエスト送信時刻・
レスポンス受信時刻・所要時間を表示する（受信時刻と所要時間は次の送信時に初期化）。
同時リクエスト数（初期値1）を指定すると、その件数を並列に送って
各リクエストの状態と個別所要時間、全体の所要時間を確認できる。
"""

from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>web (stub)</title>
  <style>
    body { font-family: sans-serif; max-width: 640px; margin: 2rem auto; }
    textarea { width: 100%; height: 6rem; }
    pre { background: #f4f4f4; padding: 1rem; white-space: pre-wrap; }
    table { border-collapse: collapse; margin: 0.5rem 0; }
    th, td { border: 1px solid #ccc; padding: 0.3rem 0.8rem; font-size: 0.9rem; }
    th { background: #f0f0f0; font-weight: normal; }
    input[type="number"] { width: 5rem; }
  </style>
</head>
<body>
  <h1>web（仮実装・テスト画面）</h1>
  <p>下のボタンがゲートウェイ <code>http://localhost:8000/api/chat</code> を直接 fetch します。</p>
  <textarea id="msg">こんにちは。1文で自己紹介して。</textarea>
  <p>
    <label>同時リクエスト数 <input id="conc" type="number" value="1" min="1" max="100"></label>
    <button id="send">AIに送る</button>
  </p>
  <table>
    <tr><th>リクエスト送信</th><td id="t-sent">−</td></tr>
    <tr><th>レスポンス受信（最後の応答）</th><td id="t-recv">−</td></tr>
    <tr><th>所要時間（全体）</th><td id="t-dur">−</td></tr>
  </table>
  <pre id="out">（ここに応答が出る）</pre>
  <script>
    const fmtTime = (d) =>
      d.toLocaleTimeString("ja-JP", { hour12: false }) +
      "." + String(d.getMilliseconds()).padStart(3, "0");

    // 1リクエストを送り、状態・個別所要時間・本文を返す（失敗もここで受け止める）
    const sendOne = async (i, message) => {
      const started = performance.now();
      try {
        const res = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: message }),
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
      const message = document.getElementById("msg").value;
      // 送信時刻を記録し、前回の受信時刻・所要時間は初期化する
      document.getElementById("t-sent").textContent = fmtTime(new Date());
      document.getElementById("t-recv").textContent = "−";
      document.getElementById("t-dur").textContent = "−";
      out.textContent = "送信中…（" + n + " 件並列）";
      const t0 = performance.now();
      const results = await Promise.all(
        Array.from({ length: n }, (_, i) => sendOne(i + 1, message))
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
      out.textContent = lines.join("\\n") + "\\n\\n--- #1 の応答本文 ---\\n" + firstBody;
    };
  </script>
</body>
</html>
"""


@app.get("/")
def index() -> str:
    return render_template_string(PAGE)
