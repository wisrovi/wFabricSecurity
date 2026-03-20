"""
Master - Envía JSON auditado (Async)
"""

import httpx
import hashlib
import json
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8002/process"

security = FabricSecurity(
    me="MASTER_ASYNC",
    use_mock=True,
)

PAYLOAD_JSON = {
    "tipo": "analisis_datos_async",
    "datos": {
        "usuario": "maria_garcia",
        "email": "maria@example.com",
        "edad": 28,
        "preferencias": ["async", "hyperledger", "python"],
    },
}


@security.master_audit(task_prefix="JSON_ASYNC", trusted_slaves=["SLAVE_ASYNC"])
async def enviar_json(payload, task_id, hash_a, sig, my_id):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, json=data, timeout=30.0)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER] Respuesta del Slave:")
    print(f"[MASTER] - Slave ID: {result['slave_id']}")
    print(f"[MASTER] - Hash B: {result['hash_b']}")
    print(f"[MASTER] - Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    import asyncio

    print("=" * 50)
    print("  MASTER JSON - Modo Async")
    print("=" * 50)
    print(f"\nEnviando a: {SLAVE_URL}\n")

    try:
        resultado = asyncio.run(enviar_json(PAYLOAD_JSON))
        print(f"\n[MASTER] ✓ Transacción completada")
    except httpx.ConnectError:
        print("\n[MASTER] ✗ Error: No se puede conectar al Slave")
        print("[MASTER] Asegúrate de que el Slave esté corriendo en el puerto 8002")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
