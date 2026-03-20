"""
Slave FastAPI - Recibe JSON auditado (Síncrono)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import hashlib
import json

app = FastAPI(title="Slave JSON - Sync")

security = None


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


def process_payload(payload):
    return {
        "procesado": True,
        "mensaje": "Datos JSON recibidos correctamente",
        "operacion": "analisis_completado",
        "timestamp": str(hashlib.sha256(str(payload).encode()).hexdigest()[:16]),
    }


@app.post("/process", response_model=ResponseData)
def process_data(data: RequestData):
    print(f"\n[SLAVE] Recibido de: {data.signer_id}")
    print(f"[SLAVE] Task ID: {data.task_id}")
    print(f"[SLAVE] Hash A: {data.hash_a[:16]}...")
    print(f"[SLAVE] Payload: {data.payload}")

    result = process_payload(data.payload)
    h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

    return ResponseData(
        result=result,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_SYNC",
    )


@app.get("/health")
def health():
    return {"status": "ok", "mode": "sync"}


@app.get("/")
def root():
    return {"service": "Slave JSON Sync", "status": "running"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE JSON - Modo Síncrono")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
