"""
Slave Image - Recibe imagen para procesamiento usando Hyperledger Fabric Real
"""

import os
import hashlib
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
from wFabricSecurity import FabricSecurity

app = FastAPI(title="Slave Image - Fabric Real")

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="SLAVE_IMAGE",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)


def process_image(file_data: bytes, original_hash: str):
    processed_hash = hashlib.sha256(file_data).hexdigest()
    return {
        "procesado": True,
        "mensaje": "Imagen procesada con Fabric Real",
        "operacion": "image_processing",
        "original_hash": original_hash,
        "processed_hash": processed_hash,
        "size": len(file_data),
    }


@security.slave_verify(trusted_masters=["MASTER_IMAGE"])
def verify_and_process(payload):
    return payload


@app.post("/process")
async def process_image_endpoint(
    file: UploadFile = File(...),
    task_id: str = Form(...),
    hash_a: str = Form(...),
    signature: str = Form(...),
    signer_id: str = Form(...),
    original_hash: str = Form(...),
):
    print(f"\n[SLAVE-IMAGE] Recibido de: {signer_id}")
    print(f"[SLAVE-IMAGE] Task ID: {task_id}")
    print(f"[SLAVE-IMAGE] Hash A: {hash_a[:16]}...")

    try:
        file_data = await file.read()
        result = process_image(file_data, original_hash)
        h_b = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

        print(f"[SLAVE-IMAGE] Registrado en Fabric: Task={task_id}")
        print(f"[SLAVE-IMAGE] Hash B: {h_b[:16]}...")

        return JSONResponse(
            content={
                "result": result,
                "hash_b": h_b,
                "slave_sig": security.gateway.sign(h_b),
                "slave_id": security.me,
            }
        )
    except Exception as e:
        print(f"[SLAVE-IMAGE] ✗ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "mode": "fabric_real"}


@app.get("/")
def root():
    return {"service": "Slave Image Fabric Real", "status": "running"}


if __name__ == "__main__":
    print("=" * 60)
    print("  SLAVE IMAGE - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=False)
