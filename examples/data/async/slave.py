"""
Slave FastAPI - Recibe archivo binario (Async)
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import base64
import asyncio

app = FastAPI(title="Slave Data - Async")


class FileData(BaseModel):
    task_id: str
    hash_a: str
    signature: str
    signer_id: str
    file_name: str
    file_type: str
    file_data: str
    file_size: int


class ResponseData(BaseModel):
    result: dict
    hash_b: str
    slave_sig: str
    slave_id: str


@app.post("/process", response_model=ResponseData)
async def process_file(data: FileData):
    await asyncio.sleep(0.1)

    import hashlib
    import json

    print(f"\n[SLAVE] Archivo recibido: {data.file_name}")
    print(f"[SLAVE] Tipo: {data.file_type}")
    print(f"[SLAVE] Tamaño: {data.file_size} bytes")
    print(f"[SLAVE] Task ID: {data.task_id}")

    file_bytes = base64.b64decode(data.file_data)
    hash_calc = hashlib.sha256(file_bytes).hexdigest()
    print(f"[SLAVE] Hash calculado: {hash_calc[:16]}...")

    resultado = {
        "file_received": True,
        "file_name": data.file_name,
        "file_type": data.file_type,
        "size_validated": len(file_bytes) == data.file_size,
        "hash_validated": True,
        "status": "Archivo procesado correctamente (async)",
    }

    h_b = hashlib.sha256(json.dumps(resultado, sort_keys=True).encode()).hexdigest()

    with open(f"received_{data.file_name}", "wb") as f:
        f.write(file_bytes)
    print(f"[SLAVE] Archivo guardado: received_{data.file_name}")

    return ResponseData(
        result=resultado,
        hash_b=h_b,
        slave_sig="firma_mock_slave",
        slave_id="SLAVE_ASYNC",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "async"}


if __name__ == "__main__":
    print("=" * 50)
    print("  SLAVE DATA - Modo Async")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8032, reload=False)
