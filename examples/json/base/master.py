"""
Master - Envía JSON auditado (Síncrono)
"""

import requests
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8001/process"

security = FabricSecurity(
    me="MASTER_SYNC",
    use_mock=True,
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


@security.master_audit(task_prefix="JSON_SYNC", trusted_slaves=["SLAVE_SYNC"])
def enviar_json(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER] Task ID: {task_id}")
    print(f"[MASTER] Hash A: {hash_a}")
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
    print(f"[MASTER] - Hash B: {result['hash_b']}")
    print(f"[MASTER] - Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTER JSON - Modo Síncrono")
    print("=" * 50)
    print(f"\nEnviando a: {SLAVE_URL}\n")

    try:
        resultado = enviar_json(PAYLOAD_JSON)
        print(f"\n[MASTER] ✓ Transacción completada")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER] ✗ Error: No se puede conectar al Slave")
        print("[MASTER] Asegúrate de que el Slave esté corriendo en el puerto 8001")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
