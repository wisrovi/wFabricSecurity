"""
Tests for wFabricSecurity - Core and Crypto Modules
"""

import os
import sys
import pytest
import hashlib
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

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


class TestCryptoModule:
    """Tests for crypto module."""

    def test_hashing_service_sha256(self):
        """Test HashingService.sha256()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.sha256("test data")
        assert result.startswith("sha256:")
        assert len(result) == 71

    def test_hashing_service_message_hash(self):
        """Test HashingService.compute_message_hash()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_message_hash("test message")
        assert result.startswith("sha256:")

    def test_hashing_service_code_hash(self):
        """Test HashingService.compute_code_hash()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            result = service.compute_code_hash([temp_file])
            assert result.startswith("sha256:")
        finally:
            os.unlink(temp_file)

    def test_hashing_service_file_hash(self):
        """Test HashingService.compute_file_hash()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content\n")
            temp_file = f.name

        try:
            result = service.compute_file_hash(temp_file)
            assert result.startswith("sha256:")
        finally:
            os.unlink(temp_file)

    def test_hashing_service_verify_hash(self):
        """Test HashingService.verify_hash()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        data = "test data"
        hash_value = service.sha256(data)
        assert service.verify_hash(data, hash_value) is True
        assert service.verify_hash("other data", hash_value) is False

    def test_hashing_service_multihash(self):
        """Test HashingService.compute_multihash()."""
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "sha256", "md5")
        assert "sha256" in result
        assert "md5" in result

    def test_signing_service_without_key(self):
        """Test SigningService without private key (fallback)."""
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        signature = service.sign("test data", "signer_id")
        assert signature is not None
        assert len(signature) > 0


class TestCoreModels:
    """Tests for core models."""

    def test_message_to_dict(self):
        """Test Message.to_dict()."""
        from wFabricSecurity import Message

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test content",
            content_hash="sha256:abc123",
            signature="sig123",
            timestamp="2024-01-01T00:00:00",
            message_id="msg123",
        )
        data = msg.to_dict()
        assert data["sender"] == "sender@test.com"
        assert data["recipient"] == "recipient@test.com"
        assert data["message_id"] == "msg123"

    def test_message_from_dict(self):
        """Test Message.from_dict()."""
        from wFabricSecurity import Message

        data = {
            "sender": "sender@test.com",
            "recipient": "recipient@test.com",
            "content": "test content",
            "content_hash": "sha256:abc123",
            "signature": "sig123",
            "timestamp": "2024-01-01T00:00:00",
            "message_id": "msg123",
        }
        msg = Message.from_dict(data)
        assert msg.sender == "sender@test.com"
        assert msg.content == "test content"

    def test_message_is_expired(self):
        """Test Message.is_expired()."""
        from wFabricSecurity import Message

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            expires_at="2023-01-01T00:00:00",
        )
        assert msg.is_expired() is True

        msg2 = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            expires_at="2099-01-01T00:00:00",
        )
        assert msg2.is_expired() is False

    def test_participant_to_dict(self):
        """Test Participant.to_dict()."""
        from wFabricSecurity import Participant, CommunicationDirection

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            version="1.0.0",
            allowed_communications=["other@test.com"],
            direction=CommunicationDirection.BIDIRECTIONAL,
        )
        data = p.to_dict()
        assert data["identity"] == "user@test.com"
        assert data["version"] == "1.0.0"
        assert "other@test.com" in data["allowed_communications"]

    def test_participant_can_communicate_with(self):
        """Test Participant.can_communicate_with()."""
        from wFabricSecurity import (
            Participant,
            CommunicationDirection,
            ParticipantStatus,
        )

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            direction=CommunicationDirection.BIDIRECTIONAL,
            is_active=True,
            status=ParticipantStatus.ACTIVE,
        )
        assert p.can_communicate_with("other@test.com") is True

        p2 = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            direction=CommunicationDirection.OUTBOUND,
            allowed_communications=["allowed@test.com"],
            is_active=True,
            status=ParticipantStatus.ACTIVE,
        )
        assert p2.can_communicate_with("allowed@test.com") is True
        assert p2.can_communicate_with("notallowed@test.com") is False

    def test_participant_is_revoked(self):
        """Test Participant.is_revoked()."""
        from wFabricSecurity import Participant, ParticipantStatus

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            status=ParticipantStatus.ACTIVE,
        )
        assert p.is_revoked() is False

        p2 = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            status=ParticipantStatus.REVOKED,
        )
        assert p2.is_revoked() is True


class TestExceptions:
    """Tests for security exceptions."""

    def test_code_integrity_error(self):
        """Test CodeIntegrityError."""
        from wFabricSecurity import CodeIntegrityError

        err = CodeIntegrityError(message="Code modified", details={"hash": "abc123"})
        assert "Code modified" in str(err)
        assert err.details["hash"] == "abc123"

    def test_permission_denied_error(self):
        """Test PermissionDeniedError."""
        from wFabricSecurity import PermissionDeniedError

        err = PermissionDeniedError(
            message="Permission denied", details={"from": "a", "to": "b"}
        )
        assert "Permission denied" in str(err)

    def test_message_integrity_error(self):
        """Test MessageIntegrityError."""
        from wFabricSecurity import MessageIntegrityError

        err = MessageIntegrityError()
        assert (
            err.message
            == "Message integrity verification failed. The message may have been altered."
        )

    def test_signature_error(self):
        """Test SignatureError."""
        from wFabricSecurity import SignatureError

        err = SignatureError()
        assert err.message == "Signature verification failed. The signature is invalid."

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        from wFabricSecurity import RateLimitError

        err = RateLimitError(message="Rate limit exceeded", details={"rps": 100})
        assert "Rate limit exceeded" in str(err)

    def test_revocation_error(self):
        """Test RevocationError."""
        from wFabricSecurity import RevocationError

        err = RevocationError(
            message="Participant revoked", details={"participant_id": "user@test.com"}
        )
        assert "revoked" in str(err).lower()


class TestEnums:
    """Tests for enums."""

    def test_communication_direction(self):
        """Test CommunicationDirection enum."""
        from wFabricSecurity import CommunicationDirection

        assert CommunicationDirection.OUTBOUND.value == "outbound"
        assert CommunicationDirection.INBOUND.value == "inbound"
        assert CommunicationDirection.BIDIRECTIONAL.value == "bidirectional"
        assert str(CommunicationDirection.OUTBOUND) == "outbound"

    def test_data_type(self):
        """Test DataType enum."""
        from wFabricSecurity import DataType

        assert DataType.JSON.value == "json"
        assert DataType.IMAGE.value == "image"
        assert DataType.P2P.value == "p2p"
        assert DataType.BINARY.value == "binary"

    def test_data_type_from_extension(self):
        """Test DataType.from_extension()."""
        from wFabricSecurity import DataType

        assert DataType.from_extension(".jpg") == DataType.IMAGE
        assert DataType.from_extension(".png") == DataType.IMAGE
        assert DataType.from_extension(".pdf") == DataType.BINARY
        assert DataType.from_extension(".json") == DataType.JSON

    def test_participant_status(self):
        """Test ParticipantStatus enum."""
        from wFabricSecurity import ParticipantStatus

        assert ParticipantStatus.ACTIVE.value == "active"
        assert ParticipantStatus.REVOKED.value == "revoked"
        assert ParticipantStatus.SUSPENDED.value == "suspended"

    def test_task_status(self):
        """Test TaskStatus enum."""
        from wFabricSecurity import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestConfigSettings:
    """Tests for configuration settings."""

    def test_settings_defaults(self):
        """Test Settings with defaults."""
        from wFabricSecurity import Settings

        settings = Settings()
        assert settings.fabric_channel == "mychannel"
        assert settings.fabric_chaincode == "tasks"
        assert settings.retry_max_attempts == 3

    def test_settings_from_env(self):
        """Test Settings.from_env()."""
        from wFabricSecurity import Settings

        os.environ["FABRIC_CHANNEL"] = "testchannel"
        os.environ["FABRIC_RETRY_MAX_ATTEMPTS"] = "5"

        settings = Settings.from_env()
        assert settings.fabric_channel == "testchannel"
        assert settings.retry_max_attempts == 5

        del os.environ["FABRIC_CHANNEL"]
        del os.environ["FABRIC_RETRY_MAX_ATTEMPTS"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
