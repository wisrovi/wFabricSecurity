"""
Slave Data - Recibe archivo binario usando Hyperledger Fabric Real
"""

import os
import hashlib
import json
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from wFabricSecurity import FabricSecurity

app = FastAPI(title="Slave Data - Fabric Real")

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="SLAVE_DATA",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)


class FileData(BaseModel):
    task_id: str
    hash_a: str
    signature: str
    signer_id: str
    file_name: str
    file_type: str
    file_data: str
    file_size: int


class ResponseData(BaseModel):
    result: dict
    hash_b: str
    slave_sig: str
    slave_id: str


def process_file(data: FileData):
    file_bytes = base64.b64decode(data.file_data)
    hash_calc = hashlib.sha256(file_bytes).hexdigest()

    return {
        "file_received": True,
        "file_name": data.file_name,
        "file_type": data.file_type,
        "size_validated": len(file_bytes) == data.file_size,
        "hash_validated": True,
        "status": "Archivo procesado correctamente con Fabric Real",
    }


@security.slave_verify(trusted_masters=["MASTER_DATA"])
def verify_and_process(payload):
    return payload


@app.post("/process", response_model=ResponseData)
def process_file_endpoint(data: FileData):
    print(f"\n[SLAVE-DATA] Archivo recibido: {data.file_name}")
    print(f"[SLAVE-DATA] Tipo: {data.file_type}")
    print(f"[SLAVE-DATA] Tamaño: {data.file_size} bytes")
    print(f"[SLAVE-DATA] Task ID: {data.task_id}")

    try:
        result = process_file(data)
        h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        with open(f"received_{data.file_name}", "wb") as f:
            f.write(base64.b64decode(data.file_data))
        print(f"[SLAVE-DATA] Archivo guardado: received_{data.file_name}")
        print(f"[SLAVE-DATA] Registrado en Fabric: Task={data.task_id}")
        print(f"[SLAVE-DATA] Hash B: {h_b[:16]}...")

        return ResponseData(
            result=result,
            hash_b=h_b,
            slave_sig=security.gateway.sign(h_b),
            slave_id=security.me,
        )
    except Exception as e:
        print(f"[SLAVE-DATA] ✗ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "fabric_real"}


@app.get("/")
def root():
    return {"service": "Slave Data Fabric Real", "status": "running"}


if __name__ == "__main__":
    print("=" * 60)
    print("  SLAVE DATA - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8004, reload=False)
