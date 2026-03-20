"""
Master - Envía archivo binario (Async)
"""

import httpx
import base64
import hashlib
import json
import os
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8032/process"

security = FabricSecurity(
    me="MASTER_DATA_ASYNC",
    use_mock=True,
)

SAMPLE_CONTENT = """
================================================================================
                    REPORTE DE MANTENIMIENTO #67890 (ASYNC)
================================================================================
Fecha: 2025-03-20
Técnico: María García
Ubicación: Planta Industrial Sur

EQUIPOS INSPECCIONADOS:
1. Turbina Eólica - Estado: Normal
2. Panel Solar - Estado: Normal
3. Inversor Grid - Estado: Requiere revisión

OBSERVACIONES:
- Limpieza de paneles realizada
- Revisión de conexiones eléctricas
- Actualización de firmware

wFabricSecurity - Asset Management (Async)
================================================================================
""".encode("utf-8")

FILE_NAME = "reporte_mantenimiento_async.txt"


@security.master_audit(task_prefix="DATA_ASYNC", trusted_slaves=["SLAVE_ASYNC"])
async def enviar_archivo(payload, task_id, hash_a, sig, my_id):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(SLAVE_URL, json=data, timeout=30.0)
        response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER] Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    import asyncio

    print("=" * 50)
    print("  MASTER DATA - Modo Async")
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
        resultado = asyncio.run(enviar_archivo(payload))
        print(f"\n[MASTER] ✓ Archivo enviado correctamente")
    except httpx.ConnectError:
        print("\n[MASTER] ✗ Error: Slave no disponible en puerto 8032")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
