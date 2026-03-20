"""
Master - Envía archivo binario (Síncrono)
"""

import requests
import base64
import hashlib
import json
import os
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8031/process"

security = FabricSecurity(
    me="MASTER_DATA_SYNC",
    use_mock=True,
)

SAMPLE_CONTENT = """
================================================================================
                    REPORTE DE MANTENIMIENTO #12345
================================================================================
Fecha: 2025-03-20
Técnico: Juan Pérez
Ubicación: Planta Industrial Norte

EQUIPOS INSPECCIONADOS:
1. Motor Principal - Estado: Normal
2. Bomba Hidráulica - Estado: Requiere atención
3. Compresor de Aire - Estado: Normal

OBSERVACIONES:
- Cambio de aceite realizado
- Filtros limpiados
- Fuga reparada

wFabricSecurity - Asset Management
================================================================================
""".encode("utf-8")

FILE_NAME = "reporte_mantenimiento.txt"


@security.master_audit(task_prefix="DATA_SYNC", trusted_slaves=["SLAVE_DATA"])
def enviar_archivo(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER] Task ID: {task_id}")
    print(f"[MASTER] Enviando archivo: {payload['file_name']}")
    print(f"[MASTER] Tipo: {payload['file_type']}")
    print(f"[MASTER] Tamaño: {payload['file_size']} bytes")

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
    print(f"\n[MASTER] Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTER DATA - Modo Síncrono")
    print("=" * 50)

    with open(FILE_NAME, "wb") as f:
        f.write(SAMPLE_CONTENT)
    print(f"[MASTER] Archivo de prueba creado: {FILE_NAME}")

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
        print(f"\n[MASTER] ✓ Archivo enviado correctamente")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER] ✗ Error: Slave no disponible en puerto 8031")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
