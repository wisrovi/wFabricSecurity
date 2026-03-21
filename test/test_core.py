"""
Tests for Core module - Exceptions, Enums, and Models
Part of Integrity Validation Matrix: Core Data Structures
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCoreExceptions:
    """Tests for core exceptions."""

    def test_security_error(self):
        from wFabricSecurity import SecurityError

        err = SecurityError("Test error")
        assert str(err) == "Test error"
        assert err.message == "Test error"

    def test_code_integrity_error(self):
        from wFabricSecurity import CodeIntegrityError

        err = CodeIntegrityError("Code modified", details={"path": "test.py"})
        assert "Code modified" in str(err)
        assert err.details["path"] == "test.py"

    def test_permission_denied_error(self):
        from wFabricSecurity import PermissionDeniedError

        err = PermissionDeniedError()
        assert "Permission denied" in str(err)

    def test_message_integrity_error(self):
        from wFabricSecurity import MessageIntegrityError

        err = MessageIntegrityError()
        assert "Message integrity" in str(err)

    def test_signature_error(self):
        from wFabricSecurity import SignatureError

        err = SignatureError()
        assert "Signature" in str(err)

    def test_rate_limit_error(self):
        from wFabricSecurity import RateLimitError

        err = RateLimitError()
        assert "Rate limit" in str(err)

    def test_revocation_error(self):
        from wFabricSecurity import RevocationError

        err = RevocationError("Revoked", details={"id": "user1"})
        assert "Revoked" in str(err)
        assert err.details["id"] == "user1"

    def test_configuration_error(self):
        from wFabricSecurity import ConfigurationError

        err = ConfigurationError("Bad config")
        assert "Bad config" in str(err)


class TestCoreEnums:
    """Tests for core enums."""

    def test_communication_direction(self):
        from wFabricSecurity import CommunicationDirection

        assert CommunicationDirection.OUTBOUND.value == "outbound"
        assert CommunicationDirection.INBOUND.value == "inbound"
        assert CommunicationDirection.BIDIRECTIONAL.value == "bidirectional"
        assert str(CommunicationDirection.OUTBOUND) == "outbound"

    def test_data_type(self):
        from wFabricSecurity import DataType

        assert DataType.JSON.value == "json"
        assert DataType.IMAGE.value == "image"
        assert DataType.P2P.value == "p2p"
        assert DataType.BINARY.value == "binary"

    def test_data_type_from_extension(self):
        from wFabricSecurity import DataType

        assert DataType.from_extension(".jpg") == DataType.IMAGE
        assert DataType.from_extension(".pdf") == DataType.BINARY
        assert DataType.from_extension(".json") == DataType.JSON

    def test_participant_status(self):
        from wFabricSecurity import ParticipantStatus

        assert ParticipantStatus.ACTIVE.value == "active"
        assert ParticipantStatus.INACTIVE.value == "inactive"
        assert ParticipantStatus.REVOKED.value == "revoked"
        assert ParticipantStatus.SUSPENDED.value == "suspended"

    def test_task_status(self):
        from wFabricSecurity import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_verification_level(self):
        from wFabricSecurity import VerificationLevel

        assert VerificationLevel.NONE.value == "none"
        assert VerificationLevel.BASIC.value == "basic"
        assert VerificationLevel.FULL.value == "full"
        assert VerificationLevel.STRICT.value == "strict"


class TestCoreModels:
    """Tests for core models."""

    def test_message_creation(self):
        from wFabricSecurity.fabric_security.core.models import Message, DataType

        msg = Message(
            sender="CN=Master",
            recipient="CN=Slave",
            content="test content",
            content_hash="hash123",
            signature="sig123",
            timestamp=datetime.now().isoformat(),
        )
        assert msg.sender == "CN=Master"
        assert msg.recipient == "CN=Slave"
        assert msg.content == "test content"

    def test_message_to_dict(self):
        from wFabricSecurity.fabric_security.core.models import Message, DataType

        msg = Message(
            sender="CN=Master",
            recipient="CN=Slave",
            content="test",
            content_hash="hash",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            message_id="msg1",
        )
        data = msg.to_dict()
        assert data["sender"] == "CN=Master"
        assert data["message_id"] == "msg1"

    def test_message_from_dict(self):
        from wFabricSecurity.fabric_security.core.models import Message, DataType

        data = {
            "sender": "CN=Master",
            "recipient": "CN=Slave",
            "content": "test",
            "content_hash": "hash",
            "signature": "sig",
            "timestamp": "2024-01-01T00:00:00",
            "message_id": "msg1",
        }
        msg = Message.from_dict(data)
        assert msg.sender == "CN=Master"
        assert msg.message_id == "msg1"

    def test_message_is_expired_true(self):
        from wFabricSecurity.fabric_security.core.models import Message

        past = (datetime.now() - timedelta(hours=1)).isoformat()
        msg = Message(
            sender="A",
            recipient="B",
            content="test",
            content_hash="h",
            signature="s",
            timestamp="now",
            expires_at=past,
        )
        assert msg.is_expired() is True

    def test_message_is_expired_false(self):
        from wFabricSecurity.fabric_security.core.models import Message

        future = (datetime.now() + timedelta(hours=1)).isoformat()
        msg = Message(
            sender="A",
            recipient="B",
            content="test",
            content_hash="h",
            signature="s",
            timestamp="now",
            expires_at=future,
        )
        assert msg.is_expired() is False

    def test_message_no_expiry(self):
        from wFabricSecurity.fabric_security.core.models import Message

        msg = Message(
            sender="A",
            recipient="B",
            content="test",
            content_hash="h",
            signature="s",
            timestamp="now",
        )
        assert msg.is_expired() is False
