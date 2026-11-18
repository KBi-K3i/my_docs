"""仮実装（スタブ）── 環境の疎通確認用。学習で本人が書き換える前提。

役割: ブラウザ/web からのリクエストを受け、LiteLLM（OpenAI互換）へ中継する。
接続先は .env の LITELLM_BASE_URL で外出し＝規模切替はアプリ無改修。
画面の「利用者ID」は user（end-user識別子）として LiteLLM へ渡し、
「仮想キー」欄が入力されたときだけ既定キー（.env）の代わりにそれを使う（開発者用）。
本番は、利用者IDを検証済みトークン由来にし、キー欄は画面に置かない。
"""

import os
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://litellm:4000")
LITELLM_KEY = os.environ.get("LITELLM_VIRTUAL_KEY", "")

app = FastAPI(title="ai-api-gateway (stub)")

# ブラウザ（web:5000 のページ）からの別オリジン fetch を許可（STEP1 の CORS 学習ポイント）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """生存確認（依存先は見ない）。"""
    return {"status": "ok"}


class ChatIn(BaseModel):
    message: str
    user: str | None = None  # 利用者ID（end-user識別子）。本番は検証済みトークン由来にする
    api_key: str | None = None  # 仮想キーの上書き（開発者用）。空なら .env の既定キー


@app.post("/api/chat")
async def chat(body: ChatIn) -> JSONResponse:
    """封筒を LiteLLM へ中継する最小の1往復（検査・整形は未実装＝学習で足す）。"""
    key = body.api_key or LITELLM_KEY
    payload: dict[str, Any] = {
        "model": "gemini",
        "messages": [{"role": "user", "content": body.message}],
    }
    if body.user:
        payload["user"] = body.user  # LiteLLM が人単位で spend を集計する識別子
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json=payload,
        )
    out: Any
    try:
        out = r.json()
    except ValueError:
        out = {"error": r.text}
    return JSONResponse(status_code=r.status_code, content=out)
