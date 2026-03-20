"""
Master Image Async - Envía imagen para procesamiento usando Hyperledger Fabric Real
"""

import os
import asyncio
import httpx
import hashlib
import json
from pathlib import Path
from wFabricSecurity import FabricSecurity

SLAVE_URL = os.getenv("SLAVE_URL", "http://127.0.0.1:8002/process")
FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_IMAGE_ASYNC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)


@security.master_audit(task_prefix="IMAGE_ASYNC", trusted_slaves=["SLAVE_IMAGE_ASYNC"])
async def enviar_imagen_async(filepath, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-IMAGE-ASYNC] Task ID: {task_id}")
    print(f"[MASTER-IMAGE-ASYNC] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-IMAGE-ASYNC] Enviando archivo: {filepath}")

    with open(filepath, "rb") as f:
        file_data = f.read()

    file_hash = hashlib.sha256(file_data).hexdigest()
    print(f"[MASTER-IMAGE-ASYNC] File hash: {file_hash[:16]}...")

    files = {
        "file": (Path(filepath).name, file_data, "image/png"),
    }
    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "original_hash": file_hash,
    }

    print(f"[MASTER-IMAGE-ASYNC] Enviando a: {SLAVE_URL}")
    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, files=files, data=data)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-IMAGE-ASYNC] Respuesta del Slave:")
    print(f"[MASTER-IMAGE-ASYNC] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-IMAGE-ASYNC] - Hash B: {result['hash_b'][:16]}...")

    return result


async def main():
    print("=" * 60)
    print("  MASTER IMAGE ASYNC - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL (ASYNC)")
    print(f"Enviando a: {SLAVE_URL}\n")

    image_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample.png")
    if not os.path.exists(image_path):
        image_path = "/home/wisrovi/Documentos/wFabricSecurity/sample.png"

    try:
        resultado = await enviar_imagen_async(image_path)
        print(f"\n[MASTER-IMAGE-ASYNC] ✓ Transacción completada")
    except FileNotFoundError:
        print(f"\n[MASTER-IMAGE-ASYNC] ✗ Error: Archivo no encontrado")
    except Exception as e:
        print(f"\n[MASTER-IMAGE-ASYNC] ✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
