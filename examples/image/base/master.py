"""
Master - Envía imagen codificada (Síncrono)
"""

import requests
import base64
import hashlib
import json
import os
from wFabricSecurity import FabricSecurity

SLAVE_URL = "http://127.0.0.1:8011/process"

security = FabricSecurity(
    me="MASTER_IMAGE",
    use_mock=True,
)


def create_sample_image():
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (300, 200), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.rectangle([20, 20, 280, 180], outline="blue", width=3)
    draw.text((50, 80), "Test Image", fill="black", font=font)
    draw.text((50, 110), "wFabricSecurity", fill="blue", font=font)
    img.save("sample.png")
    return "sample.png"


IMAGE_FILE = create_sample_image()


@security.master_audit(task_prefix="IMG_SYNC", trusted_slaves=["SLAVE_IMAGE"])
def enviar_imagen(payload, task_id, hash_a, sig, my_id):
    print(f"\n[MASTER] Task ID: {task_id}")
    print(f"[MASTER] Enviando imagen: {payload['image_name']}")

    data = {
        "task_id": task_id,
        "hash_a": hash_a,
        "signature": sig,
        "signer_id": my_id,
        "image_name": payload["image_name"],
        "image_data": payload["image_data"],
    }

    response = requests.post(SLAVE_URL, json=data)
    response.raise_for_status()

    result = response.json()
    print(f"\n[MASTER] Resultado: {result['result']}")

    return result


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTER IMAGE - Modo Síncrono")
    print("=" * 50)

    with open(IMAGE_FILE, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    payload = {
        "image_name": IMAGE_FILE,
        "image_data": image_data,
        "size": os.path.getsize(IMAGE_FILE),
    }

    try:
        resultado = enviar_imagen(payload)
        print(f"\n[MASTER] ✓ Imagen enviada correctamente")
    except requests.exceptions.ConnectionError:
        print("\n[MASTER] ✗ Error: Slave no disponible en puerto 8011")
    except Exception as e:
        print(f"\n[MASTER] ✗ Error: {e}")
