"""
Master Data - Envía archivo binario usando Hyperledger Fabric Real
"""

import os
import requests
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
    me="MASTER_DATA",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

SAMPLE_CONTENT = b"""
================================================================================
                    REPORTE DE MANTENIMIENTO #12345
================================================================================
Fecha: 2025-03-20
Tecnico: Juan Perez
Ubicacion: Planta Industrial Norte

EQUIPOS INSPECCIONADOS:
1. Motor Principal - Estado: Normal
2. Bomba Hidraulica - Estado: Requiere atencion
3. Compresor de Aire - Estado: Normal

OBSERVACIONES:
- Cambio de aceite realizado
- Filtros limpiados
- Fuga reparada

wFabricSecurity - Asset Management
================================================================================
"""

FILE_NAME = "reporte_mantenimiento.txt"


@security.master_audit(task_prefix="DATA_BASE", trusted_slaves=["SLAVE_DATA"])
def enviar_archivo(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-DATA] Task ID: {task_id}")
    print(f"[MASTER-DATA] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-DATA] Enviando archivo: {payload['file_name']}")

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

    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-DATA] Respuesta del Slave:")
    print(f"[MASTER-DATA] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-DATA] - Hash B: {result['hash_b'][:16]}...")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  MASTER DATA - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print(f"Enviando a: {SLAVE_URL}\n")

    with open(FILE_NAME, "wb") as f:
        f.write(SAMPLE_CONTENT)
    print(f"[MASTER-DATA] Archivo de prueba creado: {FILE_NAME}")

    with open(FILE_NAME, "rb") as f:
        file_data = base64.b64encode(f.read()).decode()

    payload = {
        "file_name": FILE_NAME,
        "file_type": "text/plain",
        "file_data": file_data,
        "file_size": len(SAMPLE_CONTENT),
    }

    try:
        resultado = enviar_archivo(payload)
        print(f"\n[MASTER-DATA] ✓ Archivo enviado correctamente")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER-DATA] ✗ Error: Slave no disponible en puerto 8004")
    except Exception as e:
        print(f"\n[MASTER-DATA] ✗ Error: {e}")
