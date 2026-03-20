"""
Master Image - Envía imagen para procesamiento usando Hyperledger Fabric Real
"""

import os
import requests
import hashlib
import json
from pathlib import Path
from wFabricSecurity import FabricSecurity

SLAVE_URL = os.getenv("SLAVE_URL", "http://127.0.0.1:8002/process")
FABRIC_PEER_URL = os.getenv("FABRIC_PEER_URL", "localhost:7051")
FABRIC_MSP_PATH = os.getenv(
    "FABRIC_MSP_PATH",
    "/home/wisrovi/Documentos/wFabricSecurity/enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp",
)

security = FabricSecurity(
    me="MASTER_IMAGE",
    peer_url=FABRIC_PEER_URL,
    msp_path=FABRIC_MSP_PATH,
)


@security.master_audit(task_prefix="IMAGE_BASE", trusted_slaves=["SLAVE_IMAGE"])
def enviar_imagen(filepath, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER-IMAGE] Task ID: {task_id}")
    print(f"[MASTER-IMAGE] Hash A: {hash_a[:16]}...")
    print(f"[MASTER-IMAGE] Enviando archivo: {filepath}")

    with open(filepath, "rb") as f:
        file_data = f.read()

    file_hash = hashlib.sha256(file_data).hexdigest()
    print(f"[MASTER-IMAGE] File hash: {file_hash[:16]}...")

    files = {
        "file": (Path(filepath).name, file_data, "image/png"),
    }
    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "original_hash": file_hash,
    }

    print(f"[MASTER-IMAGE] Enviando a: {SLAVE_URL}")
    response = requests.post(SLAVE_URL, files=files, data=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER-IMAGE] Respuesta del Slave:")
    print(f"[MASTER-IMAGE] - Slave ID: {result['slave_id']}")
    print(f"[MASTER-IMAGE] - Hash B: {result['hash_b'][:16]}...")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  MASTER IMAGE - Hyperledger Fabric Real")
    print("=" * 60)
    print(f"\nPeer URL: {FABRIC_PEER_URL}")
    print(f"Modo: FABRIC REAL")
    print(f"Enviando a: {SLAVE_URL}\n")

    image_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample.png")
    if not os.path.exists(image_path):
        image_path = "/home/wisrovi/Documentos/wFabricSecurity/sample.png"

    try:
        resultado = enviar_imagen(image_path)
        print(f"\n[MASTER-IMAGE] ✓ Transacción completada")
    except FileNotFoundError:
        print(f"\n[MASTER-IMAGE] ✗ Error: Archivo no encontrado: {image_path}")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER-IMAGE] ✗ Error: No se puede conectar al Slave")
        print(
            "[MASTER-IMAGE] Asegúrate de que el Slave esté corriendo en el puerto 8002"
        )
    except Exception as e:
        print(f"\n[MASTER-IMAGE] ✗ Error: {e}")
