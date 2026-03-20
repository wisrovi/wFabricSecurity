"""
Slave FastAPI - Recibe datos sensibles P2P (Síncrono)
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Slave P2P - Sync")


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
def process_p2p(data: P2PData):
    import hashlib
    import json

    print(f"\n[SLAVE] Datos P2P recibidos de: {data.signer_id}")
    print(f"[SLAVE] Task ID: {data.task_id}")
    print(f"[SLAVE] Datos sensibles:")

    for key, value in data.sensitive_data.items():
        if key in ["password", "token", "secret", "api_key"]:
            print(f"[SLAVE]   {key}: ***OCULTO***")
        else:
            print(f"[SLAVE]   {key}: {value}")

    resultado = {
        "p2p_received": True,
        "data_type": data.sensitive_data.get("data_type", "unknown"),
        "processed": True,
        "status": "Datos sensibles procesados correctamente",
    }

    h_b = hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()

    return ResponseData(
        result=resultado,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_P2P",
    )


@app.get("/health")
def health():
    return {"status": "ok", "mode": "sync"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE P2P - Modo Síncrono")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8021, reload=False)
