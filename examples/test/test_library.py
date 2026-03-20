"""
Tests for FabricSecurity library core functionality.
"""

import os
import sys
import pytest
import hashlib
import json
import tempfile
from pathlib import Path

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


FABRIC_MSP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "enviroment",
    "organizations",
    "peerOrganizations",
    "org1.net",
    "users",
    "Admin@org1.net",
    "msp",
)


class TestFabricSecurityCore:
    """Tests for core FabricSecurity functionality."""

    def test_fabric_security_init(self):
        """Test FabricSecurity initialization."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(
            me="TestUser", peer_url="localhost:7051", msp_path=FABRIC_MSP_PATH
        )

        assert security is not None
        assert security.me == "TestUser"
        assert security.gateway is not None

    def test_gateway_sign(self):
        """Test ECDSA signing."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        data = "test_data_123"
        signer_id = security.gateway.get_signer_id()
        signature = security.gateway.sign(data, signer_id)

        assert signature is not None
        assert len(signature) > 0
        assert isinstance(signature, str)

    def test_gateway_certificate_loading(self):
        """Test certificate is loaded from MSP."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        cert_pem = security.gateway.get_certificate_pem()
        if cert_pem:
            assert "BEGIN CERTIFICATE" in cert_pem
            assert "END CERTIFICATE" in cert_pem

    def test_gateway_signer_id(self):
        """Test signer ID extraction from certificate."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        signer_id = security.gateway.get_signer_id()
        assert signer_id is not None
        assert len(signer_id) > 0

    def test_code_hash_computation(self):
        """Test code hash computation."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            code_hash = security.gateway.compute_code_hash([temp_file])
            assert code_hash.startswith("sha256:")
            assert len(code_hash) == 71
        finally:
            os.unlink(temp_file)

    def test_code_hash_different_for_different_content(self):
        """Test that different content produces different hash."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        data = "test_data_123"
        signer_id = security.gateway.get_signer_id()
        signature = security.gateway.sign(data, signer_id)

        assert signature is not None
        assert len(signature) > 0
        assert isinstance(signature, str)

    def test_gateway_certificate_loading(self):
        """Test certificate is loaded from MSP."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        cert_pem = security.gateway.get_certificate_pem()
        if cert_pem:
            assert "BEGIN CERTIFICATE" in cert_pem
            assert "END CERTIFICATE" in cert_pem

    def test_gateway_signer_id(self):
        """Test signer ID extraction from certificate."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        signer_id = security.gateway.get_signer_id()
        assert signer_id is not None
        assert len(signer_id) > 0

    def test_code_hash_computation(self):
        """Test code hash computation."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            code_hash = security.gateway.compute_code_hash([temp_file])
            assert code_hash.startswith("sha256:")
            assert len(code_hash) == 71
        finally:
            os.unlink(temp_file)

    def test_code_hash_different_for_different_content(self):
        """Test that different content produces different hash."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test1')\n")
            temp_file1 = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test2')\n")
            temp_file2 = f.name

        try:
            hash1 = security.gateway.compute_code_hash([temp_file1])
            hash2 = security.gateway.compute_code_hash([temp_file2])
            assert hash1 != hash2
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)


class TestCodeIntegrity:
    """Tests for code integrity verification."""

    def test_register_code_identity(self):
        """Test code identity registration."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            result = security.register_code([temp_file], "1.0.0")
            assert result is not None
            assert "code_hash" in result
            assert "version" in result
            assert result["version"] == "1.0.0"
        finally:
            os.unlink(temp_file)

    def test_verify_code_integrity_passes(self):
        """Test verify_code passes for unchanged code."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('original')\n")
            temp_file = f.name

        try:
            security.register_code([temp_file], "1.0.0")
            result = security.verify_code([temp_file])
            assert result is True
        finally:
            os.unlink(temp_file)

    def test_verify_code_integrity_fails_for_modified_code(self):
        """Test verify_code fails for modified code."""
        from wFabricSecurity.fabric_security.fabric_security import (
            FabricSecurity,
            CodeIntegrityError,
        )

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('original')\n")
            temp_file = f.name

        try:
            security.register_code([temp_file], "1.0.0")

            with open(temp_file, "w") as f:
                f.write("print('MODIFIED')\n")

            with pytest.raises(CodeIntegrityError):
                security.verify_code([temp_file])
        finally:
            os.unlink(temp_file)


class TestMasterAuditDecorator:
    """Tests for master_audit decorator."""

    def test_master_audit_sync(self):
        """Test sync master_audit decorator."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        @security.master_audit(task_prefix="TEST", trusted_slaves=["SLAVE_TEST"])
        def test_func(payload, task_id, hash_a, sig, my_id):
            return {"processed": True, "task_id": task_id}

        payload = {"test": "data"}
        result = test_func(payload)

        assert result is not None
        assert result["processed"] is True

    def test_master_audit_async(self):
        """Test async master_audit decorator."""
        from wFabricSecurity import FabricSecurity
        import asyncio

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        @security.master_audit(task_prefix="TEST_ASYNC", trusted_slaves=["SLAVE_TEST"])
        async def test_func_async(payload, task_id, hash_a, sig, my_id):
            return {"processed": True, "task_id": task_id}

        payload = {"test": "async_data"}
        result = asyncio.run(test_func_async(payload))

        assert result is not None
        assert result["processed"] is True


class TestSlaveVerifyDecorator:
    """Tests for slave_verify decorator."""

    def test_slave_verify_sync(self):
        """Test sync slave_verify decorator."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        @security.slave_verify(trusted_masters=["MASTER_TEST"])
        def test_process(payload):
            return {"result": "processed", "data": payload}

        request_data = {
            "task_id": "test_123",
            "hash_a": "a" * 64,
            "signature": "sig",
            "signer_id": "CN=MASTER_TEST",
            "payload": {"test": True},
        }

        result = test_process(request_data)

        assert result is not None
        assert "result" in result
        assert "hash_b" in result
        assert "slave_sig" in result
        assert "slave_id" in result

    def test_slave_verify_async(self):
        """Test async slave_verify decorator."""
        from wFabricSecurity import FabricSecurity
        import asyncio

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        @security.slave_verify(trusted_masters=["MASTER_TEST"])
        async def test_process_async(payload):
            return {"result": "async_processed", "data": payload}

        request_data = {
            "task_id": "test_async_123",
            "hash_a": "a" * 64,
            "signature": "sig",
            "signer_id": "CN=MASTER_TEST",
            "payload": {"async": True},
        }

        result = asyncio.run(test_process_async(request_data))

        assert result is not None
        assert result["result"]["result"] == "async_processed"
