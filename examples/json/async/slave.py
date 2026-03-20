"""
Slave FastAPI - Recibe JSON auditado (Async)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio

app = FastAPI(title="Slave JSON - Async")


class RequestData(BaseModel):
    task_id: str
    hash_a: str
    signature: str
    signer_id: str
    payload: dict


class ResponseData(BaseModel):
    result: dict
    hash_b: str
    slave_sig: str
    slave_id: str


RESULTADO_SLAVE = {
    "procesado": True,
    "mensaje": "Datos JSON recibidos correctamente (async)",
    "operacion": "analisis_async_completado",
}


@app.post("/process", response_model=ResponseData)
async def process_data(data: RequestData):
    await asyncio.sleep(0.1)

    print(f"\n[SLAVE] Recibido de: {data.signer_id}")
    print(f"[SLAVE] Task ID: {data.task_id}")
    print(f"[SLAVE] Hash A: {data.hash_a[:16]}...")
    print(f"[SLAVE] Payload: {data.payload}")

    import hashlib
    import json

    h_b = hashlib.sha256(
        json.dumps(RESULTADO_SLAVE, sort_keys=True).encode()
    ).hexdigest()

    return ResponseData(
        result=RESULTADO_SLAVE,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_ASYNC",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "async"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE JSON - Modo Async")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
