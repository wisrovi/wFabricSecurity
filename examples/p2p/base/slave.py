"""
Slave P2P - Recibe datos sensibles usando Hyperledger Fabric Real
"""

import os
import hashlib
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from wFabricSecurity import FabricSecurity

app = FastAPI(title="Slave P2P - Fabric Real")

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="SLAVE_P2P",
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


def process_sensitive_data(payload):
    masked_payload = {**payload}
    if "datos" in masked_payload and "tarjeta_credito" in masked_payload["datos"]:
        masked_payload["datos"]["tarjeta_credito"] = "**** **** **** 1234"

    return {
        "procesado": True,
        "mensaje": "Datos sensibles procesados con Fabric Real",
        "operacion": "p2p_verificacion",
        "datos_procesados": masked_payload,
    }


@security.slave_verify(trusted_masters=["MASTER_P2P"])
def verify_and_process(payload):
    return process_sensitive_data(payload)


@app.post("/process", response_model=ResponseData)
def process_data(data: RequestData):
    print(f"\n[SLAVE-P2P] Recibido de: {data.signer_id}")
    print(f"[SLAVE-P2P] Task ID: {data.task_id}")
    print(f"[SLAVE-P2P] Hash A: {data.hash_a[:16]}...")

    try:
        result = verify_and_process(data.payload)
        h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        print(f"[SLAVE-P2P] Registrado en Fabric: Task={data.task_id}")
        print(f"[SLAVE-P2P] Hash B: {h_b[:16]}...")

        return ResponseData(
            result=result,
            hash_b=h_b,
            slave_sig=security.gateway.sign(h_b),
            slave_id=security.me,
        )
    except Exception as e:
        print(f"[SLAVE-P2P] ✗ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "fabric_real"}


@app.get("/")
def root():
    return {"service": "Slave P2P Fabric Real", "status": "running"}


if __name__ == "__main__":
    print("=" * 60)
    print("  SLAVE P2P - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8003, reload=False)
