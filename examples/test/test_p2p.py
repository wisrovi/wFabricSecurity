"""
Tests for P2P examples (base and async).
"""

import os
import sys
import pytest
import requests
import hashlib
import json
import asyncio

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


SLAVE_PORT_BASE = 9301
SLAVE_PORT_ASYNC = 9302


@pytest.fixture(scope="module")
def slave_p2p_base(slave_server):
    """Start P2P base slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "p2p", "base", "slave.py"
        ),
        SLAVE_PORT_BASE,
    )
    assert slave_server.health_check(), "Slave P2P base not healthy"
    yield slave_server


@pytest.fixture(scope="module")
def slave_p2p_async(slave_server):
    """Start P2P async slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "p2p", "async", "slave.py"
        ),
        SLAVE_PORT_ASYNC,
    )
    assert slave_server.health_check(), "Slave P2P async not healthy"
    yield slave_server


class TestP2PBase:
    """Tests for P2P base example."""

    def test_p2p_master_audit(self, slave_p2p_base, master_config):
        """Test master_audit with sensitive data payload."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_P2P_BASE", trusted_slaves=["SLAVE_P2P"]
        )
        def enviar(payload, task_id, hash_a, sig, my_id):
            data = {
                "task_id": task_id,
                "hash_a": hash_a,
                "signature": sig,
                "signer_id": my_id,
                "payload": payload,
            }
            response = requests.post(slave_p2p_base.get_url(), json=data)
            response.raise_for_status()
            return response.json()

        payload = {
            "tipo": "datos_sensibles",
            "datos": {
                "tarjeta": "**** **** **** 1234",
                "cvv": "***",
                "propietario": "Test User",
            },
        }

        result = enviar(payload)

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert "slave_sig" in result
        assert result["result"]["procesado"] is True

    def test_p2p_signature(self, slave_p2p_base, master_config):
        """Test P2P signature generation."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(**master_config)

        sensitive_data = {"secret": "very_secret_data"}
        hash_a = hashlib.sha256(
            json.dumps(sensitive_data, sort_keys=True).encode()
        ).hexdigest()
        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign(hash_a, signer_id)

        assert sig is not None
        assert len(sig) > 0
        assert len(sig) > len(hash_a)

    def test_p2p_slave_verification(self, slave_p2p_base):
        """Test that slave properly verifies and processes sensitive data."""
        data = {
            "task_id": "p2p_test_123",
            "hash_a": "a" * 64,
            "signature": "sig123",
            "signer_id": "CN=Test",
            "payload": {"tipo": "test", "datos": {"valor": 123}},
        }

        response = requests.post(slave_p2p_base.get_url(), json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["result"]["procesado"] is True


class TestP2PAsync:
    """Tests for P2P async example."""

    def test_p2p_async_master_audit(self, slave_p2p_async, master_config):
        """Test async P2P with sensitive data."""
        from wFabricSecurity import FabricSecurity
        import httpx

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_P2P_ASYNC", trusted_slaves=["SLAVE_P2P_ASYNC"]
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
                response = await client.post(slave_p2p_async.get_url(), json=data)
                response.raise_for_status()
                return response.json()

        payload = {
            "tipo": "datos_sensibles_async",
            "datos": {
                "tarjeta": "**** **** **** 5678",
                "cvv": "***",
                "propietario": "Test Async User",
            },
        }

        result = asyncio.run(enviar_async(payload))

        assert result is not None
        assert "result" in result
        assert result["result"]["procesado"] is True
