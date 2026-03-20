"""
Master JSON - Envía JSON auditado usando Hyperledger Fabric Real
"""

import os
import requests
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
    me="MASTER_JSON",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

PAYLOAD_JSON = {
    "tipo": "analisis_datos",
    "datos": {
        "usuario": "juan_perez",
        "email": "juan@example.com",
        "edad": 30,
        "preferencias": ["python", "hyperledger", "seguridad"],
    },
}


@security.master_audit(task_prefix="JSON_BASE", trusted_slaves=["SLAVE_JSON"])
def enviar_json(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER] Task ID: {task_id}")
    print(f"[MASTER] Hash A: {hash_a[:16]}...")
    print(f"[MASTER] Payload: {json.dumps(payload, indent=2)}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "payload": payload,
    }

    print(f"[MASTER] Enviando a: {SLAVE_URL}")
    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER] Respuesta del Slave:")
    print(f"[MASTER] - Slave ID: {result['slave_id']}")
    print(f"[MASTER] - Hash B: {result['hash_b'][:16]}...")
    print(f"[MASTER] - Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  MASTER JSON - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print(f"Enviando a: {SLAVE_URL}\n")

    try:
        resultado = enviar_json(PAYLOAD_JSON)
        print(f"\n[MASTER] ✓ Transacción completada")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER] ✗ Error: No se puede conectar al Slave")
        print("[MASTER] Asegúrate de que el Slave esté corriendo en el puerto 8001")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
