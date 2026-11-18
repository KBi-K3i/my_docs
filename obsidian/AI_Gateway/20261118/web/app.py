"""仮実装（スタブ）── web（Flask）の最小テスト画面。学習で本人が書き換える前提。

役割: GW開発者がテストに使う1ページを配信する。中身は3ファイルに分割してある。
画面の構造＝templates/index.html／見た目＝static/style.css／挙動＝static/app.js。
このファイル（app.py）は「ブラウザに3つを届ける配達役」だけを担う。
各ファイルが何をしているかの解説＝論点解説08（テスト画面の中身）。
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def index() -> str:
    """テスト画面（index.html）を返す。CSS/JS は Flask の static 配信が届ける。"""
    return render_template("index.html")
