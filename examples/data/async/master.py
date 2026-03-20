"""
Master Data Async - Envía archivo binario usando Hyperledger Fabric Real
"""

import os
import asyncio
import httpx
import base64
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = os.getenv("SLAVE_URL", "http://127.0.0.1:8004/process")
FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_DATA_ASYNC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

SAMPLE_CONTENT = b"""
================================================================================
                    REPORTE DE MANTENIMIENTO #67890 (ASYNC)
================================================================================
Fecha: 2025-03-20
Tecnico: Maria Garcia
Ubicacion: Planta Industrial Sur

EQUIPOS INSPECCIONADOS:
1. Turbina Eolica - Estado: Normal
2. Panel Solar - Estado: Normal
3. Inversor Grid - Estado: Requiere revision

OBSERVACIONES:
- Limpieza de paneles realizada
- Revision de conexiones electricas
- Actualizacion de firmware

wFabricSecurity - Asset Management (Async)
================================================================================
"""

FILE_NAME = "reporte_mantenimiento_async.txt"


@security.master_audit(task_prefix="DATA_ASYNC", trusted_slaves=["SLAVE_DATA_ASYNC"])
async def enviar_archivo_async(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-DATA-ASYNC] Task ID: {task_id}")
    print(f"[MASTER-DATA-ASYNC] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-DATA-ASYNC] Enviando archivo: {payload['file_name']}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "file_name": payload["file_name"],
        "file_type": payload["file_type"],
        "file_data": payload["file_data"],
        "file_size": payload["file_size"],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, json=data)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-DATA-ASYNC] Respuesta del Slave:")
    print(f"[MASTER-DATA-ASYNC] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-DATA-ASYNC] - Hash B: {result['hash_b'][:16]}...")

    return result


async def main():
    print("=" * 60)
    print("  MASTER DATA ASYNC - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL (ASYNC)")
    print(f"Enviando a: {SLAVE_URL}\n")

    with open(FILE_NAME, "wb") as f:
        f.write(SAMPLE_CONTENT)
    print(f"[MASTER-DATA-ASYNC] Archivo de prueba creado: {FILE_NAME}")

    with open(FILE_NAME, "rb") as f:
        file_data = base64.b64encode(f.read()).decode()

    payload = {
        "file_name": FILE_NAME,
        "file_type": "text/plain",
        "file_data": file_data,
        "file_size": len(SAMPLE_CONTENT),
    }

    try:
        resultado = await enviar_archivo_async(payload)
        print(f"\n[MASTER-DATA-ASYNC] ✓ Archivo enviado correctamente")
    except Exception as e:
        print(f"\n[MASTER-DATA-ASYNC] ✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
