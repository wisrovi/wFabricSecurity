"""
Master P2P - Envía datos sensibles usando Hyperledger Fabric Real
"""

import os
import requests
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
    me="MASTER_P2P",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)

PAYLOAD_SENSIBLE = {
    "tipo": "datos_sensibles",
    "datos": {
        "tarjeta_credito": "**** **** **** 1234",
        "cvv": "***",
        "fecha_expiracion": "12/25",
        "propietario": "Juan Perez",
    },
}


@security.master_audit(task_prefix="P2P_BASE", trusted_slaves=["SLAVE_P2P"])
def enviar_datos_sensibles(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-P2P] Task ID: {task_id}")
    print(f"[MASTER-P2P] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-P2P] Payload: {json.dumps(payload, indent=2)}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "payload": payload,
    }

    print(f"[MASTER-P2P] Enviando a: {SLAVE_URL}")
    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-P2P] Respuesta del Slave:")
    print(f"[MASTER-P2P] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-P2P] - Hash B: {result['hash_b'][:16]}...")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  MASTER P2P - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print(f"Enviando a: {SLAVE_URL}\n")

    try:
        resultado = enviar_datos_sensibles(PAYLOAD_SENSIBLE)
        print(f"\n[MASTER-P2P] ✓ Transacción completada")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER-P2P] ✗ Error: No se puede conectar al Slave")
        print("[MASTER-P2P] Asegúrate de que el Slave esté corriendo en el puerto 8003")
    except Exception as e:
        print(f"\n[MASTER-P2P] ✗ Error: {e}")
