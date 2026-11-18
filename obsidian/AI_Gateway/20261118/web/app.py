"""仮実装（スタブ）── web（Flask）の最小1画面。学習で本人が書き換える前提。

役割: ノートアプリの代わりの1ページを配信する。AIボタンはブラウザから
ゲートウェイ（http://localhost:8000）を直接 fetch する＝CORS の学習ポイント。
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
  </style>
</head>
<body>
  <h1>web（仮実装）</h1>
  <p>下のボタンがゲートウェイ <code>http://localhost:8000/api/chat</code> を直接 fetch します。</p>
  <textarea id="msg">こんにちは。1文で自己紹介して。</textarea>
  <p><button id="send">AIに送る</button></p>
  <pre id="out">（ここに応答が出る）</pre>
  <script>
    document.getElementById("send").onclick = async () => {
      const out = document.getElementById("out");
      out.textContent = "送信中…";
      try {
        const res = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: document.getElementById("msg").value }),
        });
        out.textContent = "HTTP " + res.status + "\\n" + JSON.stringify(await res.json(), null, 2);
      } catch (e) {
        out.textContent = "fetch 失敗: " + e;
      }
    };
  </script>
</body>
</html>
"""


@app.get("/")
def index() -> str:
    return render_template_string(PAGE)
