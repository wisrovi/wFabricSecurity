"""
Master JSON Async - Envía JSON auditado usando Hyperledger Fabric Real
"""

import os
import asyncio
import httpx
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = os.getenv("SLAVE_URL", "http://127.0.0.1:8001/process")
FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_JSON_ASYNC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

PAYLOAD_JSON = {
    "tipo": "analisis_datos_async",
    "datos": {
        "usuario": "maria_garcia",
        "email": "maria@example.com",
        "edad": 28,
        "preferencias": ["async", "fastapi", "hyperledger"],
    },
}


@security.master_audit(task_prefix="JSON_ASYNC", trusted_slaves=["SLAVE_JSON_ASYNC"])
async def enviar_json_async(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-ASYNC] Task ID: {task_id}")
    print(f"[MASTER-ASYNC] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-ASYNC] Payload: {json.dumps(payload, indent=2)}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "payload": payload,
    }

    print(f"[MASTER-ASYNC] Enviando a: {SLAVE_URL}")
    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, json=data)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-ASYNC] Respuesta del Slave:")
    print(f"[MASTER-ASYNC] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-ASYNC] - Hash B: {result['hash_b'][:16]}...")

    return result


async def main():
    print("=" * 60)
    print("  MASTER JSON ASYNC - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL (ASYNC)")
    print(f"Enviando a: {SLAVE_URL}\n")

    try:
        resultado = await enviar_json_async(PAYLOAD_JSON)
        print(f"\n[MASTER-ASYNC] ✓ Transacción completada")
    except httpx.ConnectError:
        print("\n[MASTER-ASYNC] ✗ Error: No se puede conectar al Slave")
    except Exception as e:
        print(f"\n[MASTER-ASYNC] ✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
