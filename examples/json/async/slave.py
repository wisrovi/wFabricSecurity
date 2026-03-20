"""
Slave JSON Async - Recibe JSON auditado usando Hyperledger Fabric Real
"""

import os
import hashlib
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from wFabricSecurity import FabricSecurity

app = FastAPI(title="Slave JSON Async - Fabric Real")

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="SLAVE_JSON_ASYNC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)


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
        "mensaje": "Datos JSON procesados con Fabric Real (Async)",
        "operacion": "analisis_async_completado",
        "timestamp": str(hashlib.sha256(str(payload).encode()).hexdigest()[:16]),
    }


@security.slave_verify(trusted_masters=["MASTER_JSON_ASYNC"])
def verify_and_process(payload):
    return process_payload(payload)


@app.post("/process", response_model=ResponseData)
def process_data(data: RequestData):
    print(f"\n[SLAVE-ASYNC] Recibido de: {data.signer_id}")
    print(f"[SLAVE-ASYNC] Task ID: {data.task_id}")
    print(f"[SLAVE-ASYNC] Hash A: {data.hash_a[:16]}...")

    try:
        result = verify_and_process(data.payload)
        h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        print(f"[SLAVE-ASYNC] Registrado en Fabric: Task={data.task_id}")
        print(f"[SLAVE-ASYNC] Hash B: {h_b[:16]}...")

        return ResponseData(
            result=result,
            hash_b=h_b,
            slave_sig=security.gateway.sign(h_b),
            slave_id=security.me,
        )
    except Exception as e:
        print(f"[SLAVE-ASYNC] ✗ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "fabric_real_async"}


@app.get("/")
def root():
    return {"service": "Slave JSON Async Fabric Real", "status": "running"}


if __name__ == "__main__":
    print("=" * 60)
    print("  SLAVE JSON ASYNC - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL (ASYNC)")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
