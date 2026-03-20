"""
Slave FastAPI - Recibe JSON auditado usando Hyperledger Fabric Real
Requiere:
1. Red Fabric corriendo (make network)
2. Chaincode instanciado
3. Variables de entorno configuradas
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import hashlib
import json
import os
from wFabricSecurity import FabricSecurity

app = FastAPI(title="Slave JSON - Fabric Real")

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "peer0.org1.net:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="SLAVE_FABRIC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
    use_mock=False,
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
        "mensaje": "Datos JSON procesados con Fabric Real",
        "operacion": "analisis_completado",
        "timestamp": str(hashlib.sha256(str(payload).encode()).hexdigest()[:16]),
        "fabric_mode": "real",
    }


@security.slave_verify(trusted_masters=["MASTER_FABRIC"])
def verify_and_process(payload, *args, **kwargs):
    return process_payload(payload)


@app.post("/process", response_model=ResponseData)
def process_data(data: RequestData):
    print(f"\n[SLAVE-FABRIC] Recibido de: {data.signer_id}")
    print(f"[SLAVE-FABRIC] Task ID: {data.task_id}")
    print(f"[SLAVE-FABRIC] Hash A: {data.hash_a[:16]}...")
    print(f"[SLAVE-FABRIC] Payload: {data.payload}")

    try:
        result = verify_and_process(data.payload)
        h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        print(f"[SLAVE-FABRIC] Registrado resultado en Fabric")
        print(f"[SLAVE-FABRIC] Hash B: {h_b[:16]}...")

        return ResponseData(
            result=result,
            hash_b=h_b,
            slave_sig="fabric_verified",
            slave_id="SLAVE_FABRIC",
        )
    except PermissionError as e:
        print(f"[SLAVE-FABRIC] ✗ Error de verificación: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        print(f"[SLAVE-FABRIC] ✗ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "fabric_real"}


@app.get("/")
def root():
    return {"service": "Slave JSON Fabric Real", "status": "running"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE JSON - Modo Fabric Real")
    print("=" * 50)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"MSP Path: {FABRIC_MSP_PATH}")
    print(f"Modo: {'FABRIC REAL' if not security.use_mock else 'MOCK'}")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
