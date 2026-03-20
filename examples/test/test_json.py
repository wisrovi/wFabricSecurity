"""
Tests for JSON examples (base and async).
"""

import os
import sys
import pytest
import requests
import hashlib
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


SLAVE_PORT_BASE = 9101
SLAVE_PORT_ASYNC = 9102


@pytest.fixture(scope="module")
def slave_json_base(slave_server):
    """Start JSON base slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "json", "base", "slave.py"
        ),
        SLAVE_PORT_BASE,
    )
    assert slave_server.health_check(), "Slave JSON base not healthy"
    yield slave_server


@pytest.fixture(scope="module")
def slave_json_async(slave_server):
    """Start JSON async slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "json", "async", "slave.py"
        ),
        SLAVE_PORT_ASYNC,
    )
    assert slave_server.health_check(), "Slave JSON async not healthy"
    yield slave_server


class TestJSONBase:
    """Tests for JSON base example."""

    def test_json_master_audit(self, slave_json_base, master_config):
        """Test master_audit decorator with JSON payload."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_JSON_BASE", trusted_slaves=["SLAVE_JSON"]
        )
        def enviar(payload, task_id, hash_a, sig, my_id):
            data = {
                "task_id": task_id,
                "hash_a": hash_a,
                "signature": sig,
                "signer_id": my_id,
                "payload": payload,
            }
            response = requests.post(slave_json_base.get_url(), json=data)
            response.raise_for_status()
            return response.json()

        payload = {"tipo": "test_audit", "datos": {"valor": 42, "texto": "prueba"}}

        result = enviar(payload)

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert "slave_sig" in result
        assert "slave_id" in result
        assert result["result"]["procesado"] is True

    def test_json_signature_and_hash(self, slave_json_base, master_config):
        """Test that signature and hash are properly generated."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        payload = {"test": "data"}
        hash_a = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign(hash_a, signer_id)

        assert sig is not None
        assert len(sig) > 0
        assert hash_a is not None
        assert len(hash_a) == 64

    def test_json_slave_response_structure(self, slave_json_base):
        """Test that slave returns correct response structure."""
        data = {
            "task_id": "test_task_123",
            "hash_a": "a" * 64,
            "signature": "sig123",
            "signer_id": "CN=Test",
            "payload": {"test": True},
        }

        response = requests.post(slave_json_base.get_url(), json=data)
        assert response.status_code == 200

        result = response.json()
        assert "result" in result
        assert "hash_b" in result
        assert "slave_sig" in result
        assert "slave_id" in result


class TestJSONAsync:
    """Tests for JSON async example."""

    def test_json_async_master_audit(self, slave_json_async, master_config):
        """Test master_audit decorator with async JSON payload."""
        from wFabricSecurity import FabricSecurity
        import httpx

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_JSON_ASYNC", trusted_slaves=["SLAVE_JSON_ASYNC"]
        )
        async def enviar_async(payload, task_id, hash_a, sig, my_id):
            data = {
                "task_id": task_id,
                "hash_a": hash_a,
                "signature": sig,
                "signer_id": my_id,
                "payload": payload,
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(slave_json_async.get_url(), json=data)
                response.raise_for_status()
                return response.json()

        payload = {
            "tipo": "test_async",
            "datos": {"valor": 100, "texto": "prueba async"},
        }

        result = asyncio.run(enviar_async(payload))

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert result["result"]["procesado"] is True

    def test_json_async_signature(self, slave_json_async, master_config):
        """Test async signature generation."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        payload = {"async": True}
        hash_a = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign(hash_a, signer_id)

        assert sig is not None
        assert len(sig) > 0
