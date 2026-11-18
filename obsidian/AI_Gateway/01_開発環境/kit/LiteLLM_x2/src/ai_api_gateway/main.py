"""仮実装（スタブ）── 環境の疎通確認用。学習で本人が書き換える前提。

役割: ブラウザ/web からのリクエストを受け、LiteLLM（OpenAI互換）へ中継する。
接続先は .env の LITELLM_BASE_URL（この構成=http://litellm-lb:4000）で外出し＝規模切替はアプリ無改修。
"""

import os
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://litellm-lb:4000")
LITELLM_KEY = os.environ.get("LITELLM_VIRTUAL_KEY", "")

app = FastAPI(title="ai-api-gateway (stub)")

# ブラウザ（web:5000 のページ）からの別オリジン fetch を許可（CORS の学習ポイント）
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


@app.post("/api/chat")
async def chat(body: ChatIn) -> JSONResponse:
    """封筒を LiteLLM へ中継する最小の1往復（検査・整形は未実装＝学習で足す）。"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            f"{LITELLM_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {LITELLM_KEY}"},
            json={
                "model": "gemini",
                "messages": [{"role": "user", "content": body.message}],
            },
        )
    payload: Any
    try:
        payload = r.json()
    except ValueError:
        payload = {"error": r.text}
    return JSONResponse(status_code=r.status_code, content=payload)
