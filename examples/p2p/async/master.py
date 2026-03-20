"""
Master P2P Async - Envía datos sensibles usando Hyperledger Fabric Real
"""

import os
import asyncio
import httpx
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = os.getenv("SLAVE_URL", "http://127.0.0.1:8003/process")
FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_P2P_ASYNC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

PAYLOAD_SENSIBLE = {
    "tipo": "datos_sensibles_async",
    "datos": {
        "tarjeta_credito": "**** **** **** 5678",
        "cvv": "***",
        "fecha_expiracion": "06/26",
        "propietario": "Maria Garcia",
    },
}


@security.master_audit(task_prefix="P2P_ASYNC", trusted_slaves=["SLAVE_P2P_ASYNC"])
async def enviar_datos_sensibles_async(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-P2P-ASYNC] Task ID: {task_id}")
    print(f"[MASTER-P2P-ASYNC] Hash A: {hash_a[:16]}...")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "payload": payload,
    }

    print(f"[MASTER-P2P-ASYNC] Enviando a: {SLAVE_URL}")
    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, json=data)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-P2P-ASYNC] Respuesta del Slave:")
    print(f"[MASTER-P2P-ASYNC] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-P2P-ASYNC] - Hash B: {result['hash_b'][:16]}...")

    return result


async def main():
    print("=" * 60)
    print("  MASTER P2P ASYNC - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL (ASYNC)")
    print(f"Enviando a: {SLAVE_URL}\n")

    try:
        resultado = await enviar_datos_sensibles_async(PAYLOAD_SENSIBLE)
        print(f"\n[MASTER-P2P-ASYNC] ✓ Transacción completada")
    except Exception as e:
        print(f"\n[MASTER-P2P-ASYNC] ✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
