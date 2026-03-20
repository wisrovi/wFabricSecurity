"""
Master - Envía JSON auditado usando Hyperledger Fabric Real
Requiere:
1. Red Fabric corriendo (make network)
2. Chaincode instanciado
3. Variables de entorno configuradas
"""

import requests
import hashlib
import json
import os
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8002/process"

FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "peer0.org1.net:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_FABRIC",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
    use_mock=False,
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


@security.master_audit(task_prefix="JSON_FABRIC", trusted_slaves=["SLAVE_FABRIC"])
def enviar_json(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-FABRIC] Task ID: {task_id}")
    print(f"[MASTER-FABRIC] Hash A: {hash_a}")
    print(f"[MASTER-FABRIC] Payload: {json.dumps(payload, indent=2)}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "payload": payload,
    }

    print(f"[MASTER-FABRIC] Enviando a: {SLAVE_URL}")
    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-FABRIC] Respuesta del Slave:")
    print(f"[MASTER-FABRIC] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-FABRIC] - Hash B: {result['hash_b']}")
    print(f"[MASTER-FABRIC] - Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTER JSON - Modo Fabric Real")
    print("=" * 50)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"MSP Path: {FABRIC_MSP_PATH}")
    print(f"Modo: {'FABRIC REAL' if not security.use_mock else 'MOCK'}")
    print(f"\nEnviando a: {SLAVE_URL}\n")

    try:
        resultado = enviar_json(PAYLOAD_JSON)
        print(f"\n[MASTER-FABRIC] ✓ Transacción completada")
        print(
            f"[MASTER-FABRIC] Registrado en Fabric: Task={resultado.get('task_id', 'N/A')}"
        )
    except requests.exceptions.ConnectionError:
        print("\n[MASTER-FABRIC] ✗ Error: No se puede conectar al Slave")
        print(
            "[MASTER-FABRIC] Asegúrate de que el Slave esté corriendo en el puerto 8002"
        )
    except Exception as e:
        print(f"\n[MASTER-FABRIC] ✗ Error: {e}")
