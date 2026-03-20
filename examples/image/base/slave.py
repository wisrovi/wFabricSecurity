"""
Slave FastAPI - Recibe imagen (Síncrono)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import base64

app = FastAPI(title="Slave Image - Sync")


class ImageData(BaseModel):
    task_id: str
    hash_a: str
    signature: str
    signer_id: str
    image_name: str
    image_data: str


class ResponseData(BaseModel):
    result: dict
    hash_b: str
    slave_sig: str
    slave_id: str


@app.post("/process", response_model=ResponseData)
def process_image(data: ImageData):
    import hashlib
    import json

    print(f"\n[SLAVE] Imagen recibida: {data.image_name}")
    print(f"[SLAVE] Task ID: {data.task_id}")

    image_bytes = base64.b64decode(data.image_data)
    hash_calc = hashlib.sha256(image_bytes).hexdigest()
    print(f"[SLAVE] Hash calculado: {hash_calc[:16]}...")

    resultado = {
        "image_processed": True,
        "format_detected": "png",
        "objects_found": 3,
        "analysis": "Vehículo detectado con confianza 0.95",
    }

    h_b = hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()

    with open(f"received_{data.image_name}", "wb") as f:
        f.write(image_bytes)
    print(f"[SLAVE] Imagen guardada: received_{data.image_name}")

    return ResponseData(
        result=resultado,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_IMAGE",
    )


@app.get("/health")
def health():
    return {"status": "ok", "mode": "sync"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE IMAGE - Modo Síncrono")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8011, reload=False)
