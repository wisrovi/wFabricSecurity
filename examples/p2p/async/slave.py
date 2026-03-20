"""
Slave FastAPI - Recibe datos sensibles P2P (Async)
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import asyncio

app = FastAPI(title="Slave P2P - Async")


class P2PData(BaseModel):
    task_id: str
    hash_a: str
    signature: str
    signer_id: str
    sensitive_data: dict


class ResponseData(BaseModel):
    result: dict
    hash_b: str
    slave_sig: str
    slave_id: str


@app.post("/process", response_model=ResponseData)
async def process_p2p(data: P2PData):
    await asyncio.sleep(0.1)

    import hashlib
    import json

    print(f"\n[SLAVE] Datos P2P recibidos de: {data.signer_id}")
    print(f"[SLAVE] Task ID: {data.task_id}")
    print(f"[SLAVE] Datos sensibles (async):")

    for key, value in data.sensitive_data.items():
        if key in ["password", "token", "secret", "api_key"]:
            print(f"[SLAVE]   {key}: ***OCULTO***")
        else:
            print(f"[SLAVE]   {key}: {value}")

    resultado = {
        "p2p_received": True,
        "data_type": data.sensitive_data.get("data_type", "unknown"),
        "processed": True,
        "status": "Datos sensibles procesados correctamente (async)",
    }

    h_b = hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()

    return ResponseData(
        result=resultado,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_P2P_ASYNC",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "async"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE P2P - Modo Async")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8022, reload=False)
