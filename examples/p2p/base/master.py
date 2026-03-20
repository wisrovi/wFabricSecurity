"""
Master - Envía datos sensibles P2P (Síncrono)
"""

import requests
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8021/process"

security = FabricSecurity(
    me="MASTER_P2P_SYNC",
    use_mock=True,
)

PAYLOAD_SENSITIVE = {
    "data_type": "credenciales_sistema",
    "credentials": {
        "username": "admin_sistema",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCO",
        "api_key": "sk-1234567890abcdef",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    },
    "metadata": {
        "origin": "master_node_01",
        "destination": "slave_secure_zone",
        "encryption": "AES-256",
    },
}


@security.master_audit(task_prefix="P2P_SYNC", trusted_slaves=["SLAVE_P2P"])
def enviar_datos_privados(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER] Task ID: {task_id}")
    print(f"[MASTER] Hash público (ledger): {hash_a}")
    print(f"[MASTER] Datos sensibles (solo P2P):")

    for key, value in payload.items():
        if key in ["credentials", "password", "token", "api_key"]:
            print(f"[MASTER]   {key}: ***OCULTO***")
        else:
            print(f"[MASTER]   {key}: {value}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "sensitive_data": payload,
    }

    print(f"\n[MASTER] Enviando a: {SLAVE_URL}")
    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER] Respuesta: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTER P2P - Modo Síncrono")
    print("=" * 50)
    print("\nNota: Los datos sensibles van por P2P,")
    print("      solo el hash se registra en el ledger.\n")

    try:
        resultado = enviar_datos_privados(PAYLOAD_SENSITIVE)
        print(f"\n[MASTER] ✓ Transacción P2P completada")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER] ✗ Error: Slave no disponible en puerto 8021")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
