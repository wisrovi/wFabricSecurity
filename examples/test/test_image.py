"""
Tests for Image examples (base and async).
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


SLAVE_PORT_BASE = 9201
SLAVE_PORT_ASYNC = 9202

SAMPLE_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "sample.png",
)


@pytest.fixture(scope="module")
def slave_image_base(slave_server):
    """Start Image base slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "image", "base", "slave.py"
        ),
        SLAVE_PORT_BASE,
    )
    assert slave_server.health_check(), "Slave Image base not healthy"
    yield slave_server


@pytest.fixture(scope="module")
def slave_image_async(slave_server):
    """Start Image async slave server."""
    slave_server.start(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "image", "async", "slave.py"
        ),
        SLAVE_PORT_ASYNC,
    )
    assert slave_server.health_check(), "Slave Image async not healthy"
    yield slave_server


class TestImageBase:
    """Tests for Image base example."""

    def test_image_master_audit(self, slave_image_base, master_config):
        """Test master_audit decorator with image payload."""
        from wFabricSecurity import FabricSecurity

        if not os.path.exists(SAMPLE_IMAGE_PATH):
            pytest.skip(f"Sample image not found at {SAMPLE_IMAGE_PATH}")

        with open(SAMPLE_IMAGE_PATH, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_IMAGE_BASE", trusted_slaves=["SLAVE_IMAGE"]
        )
        def enviar(payload, task_id, hash_a, sig, my_id):
            data = {
                "task_id": task_id,
                "hash_a": hash_a,
                "signature": sig,
                "signer_id": my_id,
                "payload": payload,
            }
            response = requests.post(slave_image_base.get_url(), json=data)
            response.raise_for_status()
            return response.json()

        payload = {
            "image_name": "sample.png",
            "image_data": image_data,
            "image_type": "image/png",
        }

        result = enviar(payload)

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert result["result"]["processed"] is True

    def test_image_hash_generation(self, master_config):
        """Test that image hash is properly generated."""
        from wFabricSecurity import FabricSecurity

        if not os.path.exists(SAMPLE_IMAGE_PATH):
            pytest.skip(f"Sample image not found")

        security = FabricSecurity(**master_config)

        with open(SAMPLE_IMAGE_PATH, "rb") as f:
            image_bytes = f.read()

        hash_a = hashlib.sha256(image_bytes).hexdigest()
        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign(hash_a, signer_id)

        assert sig is not None
        assert len(sig) > 0
        assert hash_a is not None
        assert len(hash_a) == 64


class TestImageAsync:
    """Tests for Image async example."""

    def test_image_async_master_audit(self, slave_image_async, master_config):
        """Test async image processing."""
        from wFabricSecurity import FabricSecurity
        import httpx

        if not os.path.exists(SAMPLE_IMAGE_PATH):
            pytest.skip(f"Sample image not found")

        with open(SAMPLE_IMAGE_PATH, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        security = FabricSecurity(**master_config)

        @security.master_audit(
            task_prefix="TEST_IMAGE_ASYNC", trusted_slaves=["SLAVE_IMAGE_ASYNC"]
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
                response = await client.post(slave_image_async.get_url(), json=data)
                response.raise_for_status()
                return response.json()

        payload = {
            "image_name": "sample.png",
            "image_data": image_data,
            "image_type": "image/png",
        }

        result = asyncio.run(enviar_async(payload))

        assert result is not None
        assert "result" in result
        assert result["result"]["processed"] is True
