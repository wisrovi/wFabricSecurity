"""
Tests for Data examples (base and async).
"""

import os
import sys
import pytest
import requests
import hashlib
import json
import base64
import asyncio
from pathlib import Path

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


SLAVE_PORT_BASE = 9401
SLAVE_PORT_ASYNC = 9402

SAMPLE_DATA = b"""
================================================================================
                    REPORTE DE TEST #12345
================================================================================
Fecha: 2026-03-21
Tecnico: Test User
Ubicacion: Test Location

EQUIPOS INSPECCIONADOS:
1. Motor Principal - Estado: Normal
2. Bomba Hidraulica - Estado: Normal

OBSERVACIONES:
- Test completado exitosamente

wFabricSecurity - Asset Management Test
================================================================================
"""


@pytest.fixture(scope="module")
def slave_data_base(slave_server):
    """Start Data base slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "base", "slave.py"
        ),
        SLAVE_PORT_BASE,
    )
    assert slave_server.health_check(), "Slave Data base not healthy"
    yield slave_server


@pytest.fixture(scope="module")
def slave_data_async(slave_server):
    """Start Data async slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "async", "slave.py"
        ),
        SLAVE_PORT_ASYNC,
    )
    assert slave_server.health_check(), "Slave Data async not healthy"
    yield slave_server


class TestDataBase:
    """Tests for Data base example."""

    def test_data_master_audit(self, slave_data_base, master_config):
        """Test master_audit with file data payload."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_DATA_BASE", trusted_slaves=["SLAVE_DATA"]
        )
        def enviar(payload, task_id, hash_a, sig, my_id):
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
            response = requests.post(slave_data_base.get_url(), json=data)
            response.raise_for_status()
            return response.json()

        payload = {
            "file_name": "test_report.txt",
            "file_type": "text/plain",
            "file_data": base64.b64encode(SAMPLE_DATA).decode(),
            "file_size": len(SAMPLE_DATA),
        }

        result = enviar(payload)

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert result["result"]["file_received"] is True
        assert result["result"]["size_validated"] is True

    def test_data_hash_generation(self, master_config):
        """Test data hash generation."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        hash_a = hashlib.sha256(SAMPLE_DATA).hexdigest()
        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign(hash_a, signer_id)

        assert sig is not None
        assert len(sig) > 0
        assert hash_a is not None
        assert len(hash_a) == 64

    def test_data_file_processing(self, slave_data_base):
        """Test file processing by slave."""
        data = {
            "task_id": "data_test_123",
            "hash_a": "a" * 64,
            "signature": "sig123",
            "signer_id": "CN=Test",
            "file_name": "test.txt",
            "file_type": "text/plain",
            "file_data": base64.b64encode(b"Hello Test").decode(),
            "file_size": 10,
        }

        response = requests.post(slave_data_base.get_url(), json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["result"]["file_received"] is True
        assert result["result"]["size_validated"] is True


class TestDataAsync:
    """Tests for Data async example."""

    def test_data_async_master_audit(self, slave_data_async, master_config):
        """Test async data file processing."""
        from wFabricSecurity import FabricSecurity
        import httpx

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_DATA_ASYNC", trusted_slaves=["SLAVE_DATA_ASYNC"]
        )
        async def enviar_async(payload, task_id, hash_a, sig, my_id):
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
                response = await client.post(slave_data_async.get_url(), json=data)
                response.raise_for_status()
                return response.json()

        payload = {
            "file_name": "async_report.txt",
            "file_type": "text/plain",
            "file_data": base64.b64encode(SAMPLE_DATA).decode(),
            "file_size": len(SAMPLE_DATA),
        }

        result = asyncio.run(enviar_async(payload))

        assert result is not None
        assert "result" in result
        assert result["result"]["file_received"] is True
        assert result["result"]["size_validated"] is True
