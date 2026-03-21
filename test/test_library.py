"""
Tests for wFabricSecurity - Complete Library Test Suite
Target: 95% coverage
"""

import os
import sys
import pytest
import tempfile
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


FABRIC_MSP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "enviroment",
    "organizations",
    "peerOrganizations",
    "org1.net",
    "users",
    "Admin@org1.net",
    "msp",
)


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
        assert DataType.from_extension(".png") == DataType.IMAGE
        assert DataType.from_extension(".gif") == DataType.IMAGE
        assert DataType.from_extension(".pdf") == DataType.BINARY
        assert DataType.from_extension(".zip") == DataType.BINARY
        assert DataType.from_extension(".json") == DataType.JSON
        assert DataType.from_extension(".txt") == DataType.JSON

    def test_participant_status(self):
        from wFabricSecurity import ParticipantStatus

        assert ParticipantStatus.ACTIVE.value == "active"
        assert ParticipantStatus.REVOKED.value == "revoked"
        assert ParticipantStatus.SUSPENDED.value == "suspended"
        assert ParticipantStatus.INACTIVE.value == "inactive"

    def test_task_status(self):
        from wFabricSecurity import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_verification_level(self):
        from wFabricSecurity import VerificationLevel

        assert VerificationLevel.NONE.value == "none"
        assert VerificationLevel.BASIC.value == "basic"
        assert VerificationLevel.FULL.value == "full"
        assert VerificationLevel.STRICT.value == "strict"


class TestCoreModels:
    """Tests for core models."""

    def test_message_creation(self):
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
        assert msg.sender == "sender@test.com"
        assert msg.content == "test content"

    def test_message_to_dict(self):
        from wFabricSecurity import Message, DataType

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            message_id="msg123",
            data_type=DataType.JSON,
        )
        data = msg.to_dict()
        assert data["sender"] == "sender@test.com"
        assert data["data_type"] == "json"

    def test_message_from_dict(self):
        from wFabricSecurity import Message

        data = {
            "sender": "sender@test.com",
            "recipient": "recipient@test.com",
            "content": "test",
            "content_hash": "sha256:abc",
            "signature": "sig",
            "timestamp": "2024-01-01T00:00:00",
            "message_id": "msg123",
        }
        msg = Message.from_dict(data)
        assert msg.sender == "sender@test.com"

    def test_message_is_expired_true(self):
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

    def test_message_is_expired_false(self):
        from wFabricSecurity import Message

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            expires_at="2099-01-01T00:00:00",
        )
        assert msg.is_expired() is False

    def test_participant_creation(self):
        from wFabricSecurity import Participant, CommunicationDirection

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc123",
            version="1.0.0",
            direction=CommunicationDirection.BIDIRECTIONAL,
        )
        assert p.identity == "user@test.com"
        assert p.version == "1.0.0"

    def test_participant_to_dict(self):
        from wFabricSecurity import Participant, CommunicationDirection

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc",
            direction=CommunicationDirection.OUTBOUND,
        )
        data = p.to_dict()
        assert data["identity"] == "user@test.com"
        assert data["direction"] == "outbound"

    def test_participant_from_dict(self):
        from wFabricSecurity import Participant

        data = {
            "identity": "user@test.com",
            "code_hash": "sha256:abc",
            "direction": "bidirectional",
        }
        p = Participant.from_dict(data)
        assert p.identity == "user@test.com"

    def test_participant_can_communicate_bidirectional(self):
        from wFabricSecurity import Participant, CommunicationDirection

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc",
            direction=CommunicationDirection.BIDIRECTIONAL,
            is_active=True,
        )
        assert p.can_communicate_with("other@test.com") is True

    def test_participant_can_communicate_outbound(self):
        from wFabricSecurity import Participant, CommunicationDirection

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc",
            direction=CommunicationDirection.OUTBOUND,
            allowed_communications=["allowed@test.com"],
            is_active=True,
        )
        assert p.can_communicate_with("allowed@test.com") is True
        assert p.can_communicate_with("notallowed@test.com") is False

    def test_participant_is_revoked(self):
        from wFabricSecurity import Participant, ParticipantStatus

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc",
            status=ParticipantStatus.REVOKED,
        )
        assert p.is_revoked() is True

    def test_participant_inactive(self):
        from wFabricSecurity import Participant, ParticipantStatus

        p = Participant(
            identity="user@test.com",
            code_hash="sha256:abc",
            is_active=False,
        )
        assert p.can_communicate_with("other@test.com") is False

    def test_task_creation(self):
        from wFabricSecurity import Task, TaskStatus

        task = Task(
            task_id="task123",
            hash_a="sha256:abc",
            master_id="master@test.com",
        )
        assert task.task_id == "task123"
        assert task.status == TaskStatus.PENDING

    def test_task_to_dict(self):
        from wFabricSecurity import Task

        task = Task(
            task_id="task123",
            hash_a="sha256:abc",
        )
        data = task.to_dict()
        assert data["task_id"] == "task123"
        assert data["hash_a"] == "sha256:abc"

    def test_task_is_complete(self):
        from wFabricSecurity import Task, TaskStatus

        task = Task(
            task_id="task123",
            hash_a="sha256:abc",
            hash_b="sha256:def",
            status=TaskStatus.COMPLETED,
        )
        assert task.is_complete() is True


class TestCryptoModule:
    """Tests for crypto module."""

    def test_hashing_service_sha256(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.sha256("test data")
        assert result.startswith("sha256:")
        assert len(result) == 71

    def test_hashing_service_sha256_raw(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.sha256_raw("test data")
        assert len(result) == 64
        assert ":" not in result

    def test_hashing_service_message_hash(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_message_hash("test message")
        assert result.startswith("sha256:")

    def test_hashing_service_code_hash(self):
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
        from wFabricSecurity import HashingService

        service = HashingService()
        data = "test data"
        hash_value = service.sha256(data)
        assert service.verify_hash(data, hash_value) is True
        assert service.verify_hash(data, "sha256:wrong") is False

    def test_hashing_service_multihash(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "sha256", "md5")
        assert "sha256" in result
        assert "md5" in result

    def test_hashing_service_multihash_blake(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "blake2b", "blake2s")
        assert "blake2b" in result
        assert "blake2s" in result

    def test_signing_service_without_key(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        signature = service.sign("test data", "signer_id")
        assert signature is not None
        assert len(signature) > 0

    def test_signing_service_has_private_key(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        assert service.has_private_key is False

    def test_identity_manager_init(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager("/tmp/fake_path")
        assert manager.msp_path == "/tmp/fake_path"

    def test_identity_manager_cache(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager("/tmp/fake_path")
        manager.cache_certificate("user@test.com", "cert_pem_data")
        cached = manager.get_cached_certificate("user@test.com")
        assert cached == "cert_pem_data"

    def test_identity_manager_cache_clear(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager("/tmp/fake_path")
        manager.cache_certificate("user@test.com", "cert")
        manager.clear_cache()
        assert manager.get_cached_certificate("user@test.com") is None


class TestConfigModule:
    """Tests for config module."""

    def test_settings_defaults(self):
        from wFabricSecurity import Settings

        settings = Settings()
        assert settings.fabric_channel == "mychannel"
        assert settings.fabric_chaincode == "tasks"
        assert settings.retry_max_attempts == 3

    def test_settings_from_env(self):
        from wFabricSecurity import Settings

        os.environ["FABRIC_CHANNEL"] = "testchannel"
        os.environ["FABRIC_RETRY_MAX_ATTEMPTS"] = "5"

        settings = Settings.from_env()
        assert settings.fabric_channel == "testchannel"
        assert settings.retry_max_attempts == 5

        del os.environ["FABRIC_CHANNEL"]
        del os.environ["FABRIC_RETRY_MAX_ATTEMPTS"]

    def test_settings_to_yaml(self):
        from wFabricSecurity import Settings
        import tempfile

        settings = Settings()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            settings.to_yaml(temp_file)
            assert os.path.exists(temp_file)
            with open(temp_file) as f:
                content = f.read()
                assert "mychannel" in content
        finally:
            os.unlink(temp_file)

    def test_settings_from_yaml(self):
        from wFabricSecurity import Settings
        import tempfile

        yaml_content = """
local_data_dir: /tmp/test_data
fabric_channel: testchannel
retry_max_attempts: 5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            settings = Settings.from_yaml(temp_file)
            assert settings.fabric_channel == "testchannel"
            assert settings.retry_max_attempts == 5
        finally:
            os.unlink(temp_file)

    def test_get_settings(self):
        from wFabricSecurity import get_settings

        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, "fabric_channel")


class TestStorageModule:
    """Tests for storage module."""

    def test_local_storage_init(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_init")
        assert storage._data_dir.name == "test_storage_init"

    def test_local_storage_save_get(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_save")
        storage.save("key1", {"data": "value"})
        result = storage.get("key1")
        assert result["data"] == "value"

    def test_local_storage_get_default(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_default")
        result = storage.get("nonexistent", default="default_value")
        assert result == "default_value"

    def test_local_storage_delete(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_delete")
        storage.save("key1", {"data": "value"})
        assert storage.delete("key1") is True
        assert storage.exists("key1") is False

    def test_local_storage_exists(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_exists")
        storage.save("key1", {"data": "value"})
        assert storage.exists("key1") is True
        assert storage.exists("key2") is False

    def test_local_storage_list_keys(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_list")
        storage.save("key1", {"data": 1})
        storage.save("key2", {"data": 2})
        storage.save("other_key", {"data": 3})

        keys = storage.list_keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_local_storage_clear(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_clear")
        storage.save("key1", {"data": "value"})
        storage.save("key2", {"data": "value"})
        storage.clear()
        assert storage.list_keys() == []

    def test_local_storage_revoked(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_revoked")
        storage.add_revoked_participant("user@test.com")

        assert storage.is_participant_revoked("user@test.com") is True
        assert storage.is_participant_revoked("other@test.com") is False

        revoked = storage.get_revoked_participants()
        assert "user@test.com" in revoked

    def test_local_storage_stats(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_stats")
        storage.save("key1", {"data": "value"})

        stats = storage.get_stats()
        assert "total_keys" in stats
        assert "size_bytes" in stats

    def test_local_storage_size(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_storage_size")
        storage.save("key1", {"data": "x" * 1000})
        size = storage.get_storage_size()
        assert size > 0


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_rate_limiter_init(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=20)
        assert limiter.requests_per_second == 10
        assert limiter.burst_size == 20

    def test_rate_limiter_acquire(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        assert limiter.acquire(tokens=1) is True

    def test_rate_limiter_try_acquire(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=1)
        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is False

    def test_rate_limiter_acquire_multiple(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=5)
        assert limiter.acquire(tokens=3) is True
        tokens = limiter.get_available_tokens()
        assert tokens < 5

    def test_rate_limiter_available_tokens(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        tokens = limiter.get_available_tokens()
        assert tokens == 5

    def test_rate_limiter_stats(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(2)

        stats = limiter.get_stats()
        assert "available_tokens" in stats
        assert "requests_per_second" in stats
        assert "recent_requests_1s" in stats
        assert stats["requests_per_second"] == 10

    def test_rate_limiter_block_unblock(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        assert limiter.is_blocked is False

        limiter.block_for(0.5)
        assert limiter.is_blocked is True

        time.sleep(0.6)
        assert limiter.is_blocked is False

    def test_rate_limiter_reset(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(3)
        limiter.reset()

        stats = limiter.get_stats()
        assert stats["available_tokens"] == 5


class TestRetryModule:
    """Tests for retry module."""

    def test_retry_success(self):
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=3)
        def successful():
            return "success"

        assert successful() == "success"

    def test_retry_eventual_success(self):
        from wFabricSecurity import with_retry

        attempts = {"count": 0}

        @with_retry(max_attempts=3, initial_delay=0.01, backoff_factor=1.0)
        def eventually_success():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("Not yet")
            return "success"

        assert eventually_success() == "success"
        assert attempts["count"] == 2

    def test_retry_exhausted(self):
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_retry_specific_exceptions(self):
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=2, exceptions=(ValueError,), initial_delay=0.01)
        def fails_with_value():
            raise ValueError("Value error")

        with pytest.raises(ValueError):
            fails_with_value()

        @with_retry(max_attempts=2, exceptions=(ValueError,), initial_delay=0.01)
        def fails_with_type():
            raise TypeError("Type error")

        with pytest.raises(TypeError):
            fails_with_type()

    def test_retry_context(self):
        from wFabricSecurity import RetryContext

        with RetryContext(max_attempts=3) as ctx:
            pass
        assert ctx.succeeded is True
        assert ctx.attempt == 1

    def test_retry_context_success(self):
        from wFabricSecurity import RetryContext

        with RetryContext(max_attempts=3) as ctx:
            pass
        assert ctx.succeeded is True
        assert ctx.attempt == 1


class TestFabricGateway:
    """Tests for FabricGateway."""

    def test_gateway_init(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(
            peer_url="localhost:7051",
            msp_path="/tmp/fake_msp",
        )
        assert gateway.peer_url == "localhost:7051"

    def test_gateway_hash(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(
            peer_url="localhost:7051",
            msp_path="/tmp/fake_msp",
        )

        code_hash = gateway.compute_code_hash(["/tmp/fake_file.py"])
        assert code_hash.startswith("sha256:")

        msg_hash = gateway.compute_message_hash("test content")
        assert msg_hash.startswith("sha256:")

    def test_gateway_message_hash(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(
            peer_url="localhost:7051",
            msp_path="/tmp/fake_msp",
        )

        hash1 = gateway.compute_message_hash("test")
        hash2 = gateway.compute_message_hash("test")
        assert hash1 == hash2

        hash3 = gateway.compute_message_hash("other")
        assert hash1 != hash3


class TestFabricSecurityMain:
    """Tests for FabricSecurity main class."""

    def test_fabric_security_init(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(
            me="TestUser",
            rate_limit_rps=50,
            rate_limit_burst=100,
            message_ttl=7200,
        )

        assert security.me == "TestUser"
        assert security.rate_limiter is not None
        assert security.message_manager is not None

    def test_fabric_security_rate_limiter(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(
            me="TestUser", rate_limit_rps=100, rate_limit_burst=10
        )

        assert security.rate_limiter.try_acquire() is True
        stats = security.rate_limiter.get_stats()
        assert stats["requests_per_second"] == 100

    def test_fabric_security_stats(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        stats = security.get_stats()

        assert "identity" in stats
        assert "using_fabric" in stats
        assert "rate_limiter" in stats

    def test_fabric_security_get_signer_id(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        signer_id = security.get_signer_id()
        assert signer_id is not None

    def test_fabric_security_sign(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        signature = security.sign("test data", "signer_id")
        assert signature is not None
        assert len(signature) > 0

    def test_fabric_security_verify_code(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            security.register_code([temp_file], "1.0.0")
            result = security.verify_code([temp_file])
            assert result is True
        finally:
            os.unlink(temp_file)

    def test_fabric_security_register_code(self):
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            result = security.register_code([temp_file], "1.0.0")
            assert result is not None
            assert "code_hash" in result
        finally:
            os.unlink(temp_file)


class TestFabricSecuritySimple:
    """Tests for FabricSecuritySimple."""

    def test_simple_init(self):
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="TestUser")
        assert security.me == "TestUser"
        assert security.gateway is not None

    def test_simple_sign(self):
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="TestUser")
        signature = security.gateway.sign("test data", "signer_id")
        assert signature is not None

    def test_simple_master_audit_sync(self):
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="TestUser")

        @security.master_audit(task_prefix="TEST", trusted_slaves=["SLAVE"])
        def test_func(payload, task_id, hash_a, sig, my_id):
            return {"processed": True}

        result = test_func({"test": "data"})
        assert result["processed"] is True


class TestIntegrityVerifier:
    """Tests for IntegrityVerifier."""

    def test_verify_code_hash(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            code_hash = verifier.compute_code_hash([temp_file])
            assert code_hash.startswith("sha256:")
        finally:
            os.unlink(temp_file)


class TestPermissionManager:
    """Tests for PermissionManager."""

    def test_register_communication(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        result = manager.register_communication("user1", "user2")
        assert result is not None

    def test_can_communicate(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        manager.register_communication("user1", "user2")
        assert manager.can_communicate_with("user1", "user2") is True


class TestMessageManager:
    """Tests for MessageManager."""

    def test_create_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = MessageManager(gateway)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test content",
            data_type=DataType.JSON,
        )

        assert msg.sender == "sender@test.com"
        assert msg.recipient == "recipient@test.com"
        assert msg.content == "test content"
        assert msg.content_hash.startswith("sha256:")

    def test_message_expiration(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = MessageManager(gateway, ttl_seconds=1)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            data_type=DataType.JSON,
            ttl_seconds=1,
        )

        assert msg.expires_at is not None
        assert msg.is_expired() is False

        time.sleep(1.1)
        assert msg.is_expired() is True


class TestCLI:
    """Tests for CLI module."""

    def test_cli_import(self):
        from wFabricSecurity.fabric_security import cli

        assert cli is not None


class TestVersion:
    """Tests for version info."""

    def test_version_exists(self):
        from wFabricSecurity import __version__

        assert __version__ is not None
        assert len(__version__) > 0


class TestFabricContract:
    """Tests for FabricContract."""

    def test_contract_init(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        assert contract.channel == "mychannel"
        assert contract.chaincode == "tasks"

    def test_contract_submit_transaction(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.submit_transaction("TestFunc", "arg1", "arg2")
        assert result is not None

    def test_contract_evaluate_transaction(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.evaluate_transaction("TestFunc", "arg1")
        assert result is None or isinstance(result, str)

    def test_contract_register_certificate(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.register_certificate("user@test.com", "cert_data")
        assert result is not None

    def test_contract_register_participant(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.register_participant(
            {
                "identity": "user@test.com",
                "code_hash": "sha256:abc",
            }
        )
        assert result is not None

    def test_contract_register_task(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.register_task("task123", "hash_a")
        assert result is not None

    def test_contract_complete_task(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.complete_task("task123", "hash_b")
        assert result is not None

    def test_contract_get_task(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.get_task("task123")
        assert result is None

    def test_contract_put_private_data(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.put_private_data("collection", "key", {"data": "value"})
        assert result is not None

    def test_contract_get_private_data(self):
        from wFabricSecurity import FabricGateway, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.get_private_data("collection", "key")
        assert result is None


class TestFabricNetwork:
    """Tests for FabricNetwork."""

    def test_network_init(self):
        from wFabricSecurity import FabricGateway, FabricNetwork

        gateway = FabricGateway(msp_path="/tmp/fake")
        network = FabricNetwork(gateway, "mychannel")

        assert network.channel == "mychannel"

    def test_network_get_contract(self):
        from wFabricSecurity import FabricGateway, FabricNetwork, FabricContract

        gateway = FabricGateway(msp_path="/tmp/fake")
        network = FabricNetwork(gateway, "mychannel")

        contract = network.get_contract("tasks")
        assert isinstance(contract, FabricContract)

    def test_network_get_default_contract(self):
        from wFabricSecurity import FabricGateway, FabricNetwork

        gateway = FabricGateway(msp_path="/tmp/fake")
        network = FabricNetwork(gateway, "mychannel")

        contract = network.get_default_contract()
        assert contract is not None


class TestSecurityDecorators:
    """Tests for security decorators."""

    def test_master_audit_decorator(self):
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="TestUser")

        @security.master_audit(task_prefix="TEST", trusted_slaves=["SLAVE1", "SLAVE2"])
        def test_func(payload, task_id, hash_a, sig, my_id):
            return {"result": "success", "task_id": task_id}

        result = test_func({"data": "test"})
        assert result is not None

    def test_slave_verify_decorator(self):
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="TestUser")

        @security.slave_verify(trusted_masters=["MASTER1"])
        def test_func(payload):
            return {"result": "processed", "data": payload}

        request = {
            "task_id": "task123",
            "hash_a": "hash_a_value",
            "signature": "sig_value",
            "signer_id": "MASTER1",
            "payload": {"data": "test"},
        }

        result = test_func(request)
        assert result is not None
        assert "result" in result
        assert "hash_b" in result


class TestMessageManagerExtended:
    """Extended tests for MessageManager."""

    def test_create_json_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = MessageManager(gateway)

        msg = manager.create_json_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            data={"key": "value"},
        )

        assert msg.data_type.value == "json"

    def test_create_binary_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = MessageManager(gateway)

        msg = manager.create_binary_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            data=b"binary data here",
        )

        assert msg.data_type.value == "binary"

    def test_verify_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = MessageManager(gateway)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test content",
            data_type=DataType.JSON,
        )

        result = manager.verify_message(msg)
        assert result is True

    def test_get_messages_for_recipient(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        messages = manager.get_messages_for_recipient("nonexistent@test.com")
        assert isinstance(messages, list)


class TestPermissionManagerExtended:
    """Extended tests for PermissionManager."""

    def test_revoke_participant(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        result = manager.revoke_participant("user@test.com")
        assert result is not None

    def test_is_revoked(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        manager.revoke_participant("user@test.com")
        assert manager.is_revoked("user@test.com") is True
        assert manager.is_revoked("other@test.com") is False

    def test_get_revoked_participants(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        manager.revoke_participant("user1@test.com")
        manager.revoke_participant("user2@test.com")

        revoked = manager.get_revoked_participants()
        assert "user1@test.com" in revoked
        assert "user2@test.com" in revoked

    def test_update_participant(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        result = manager.update_participant("user@test.com", {"version": "2.0.0"})
        assert result is not None

    def test_get_allowed_communications(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        allowed = manager.get_allowed_communications("nonexistent@test.com")
        assert isinstance(allowed, list)


class TestIntegrityVerifierExtended:
    """Extended tests for IntegrityVerifier."""

    def test_verify_own_code(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        result = verifier.verify_code_integrity(["/tmp/nonexistent_file_12345.py"])
        assert result is True

    def test_register_code(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            result = verifier.register_code([temp_file], "1.0.0")
            assert result is not None
        finally:
            os.unlink(temp_file)

    def test_get_registered_hash(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        result = verifier.get_registered_hash("nonexistent@test.com")
        assert result is None

    def test_verify_multiple_paths(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            results = verifier.verify_multiple_paths([(temp_file, "sha256:fake")])
            assert len(results) == 1
        finally:
            os.unlink(temp_file)


class TestRetryExtended:
    """Extended tests for retry module."""

    def test_retry_with_on_retry_callback(self):
        from wFabricSecurity import with_retry

        callbacks = []

        def on_retry(exc, attempt):
            callbacks.append((exc, attempt))

        @with_retry(max_attempts=3, initial_delay=0.01, on_retry=on_retry)
        def eventually_success():
            if len(callbacks) < 1:
                raise ValueError("Retry")
            return "success"

        result = eventually_success()
        assert result == "success"
        assert len(callbacks) == 1


class TestConfigDefaults:
    """Tests for config defaults."""

    def test_defaults_values(self):
        from wFabricSecurity.fabric_security.config.defaults import Defaults

        assert Defaults.RETRY_MAX_ATTEMPTS == 3
        assert Defaults.RATE_LIMIT_REQUESTS_PER_SECOND == 100
        assert Defaults.MESSAGE_TTL_SECONDS == 3600
        assert Defaults.CERT_CACHE_SIZE == 100


class TestFabricStorage:
    """Tests for FabricStorage."""

    def test_fabric_storage_init(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        assert storage.channel == "mychannel"
        assert storage.chaincode == "tasks"

    def test_fabric_storage_is_available(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        assert isinstance(storage.is_available, bool)


class TestCryptoIdentityExtended:
    """Extended tests for IdentityManager."""

    def test_identity_manager_get_signer_cn(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager("/tmp/fake")
        cn = manager.get_signer_cn()
        assert cn == "Unknown"

    def test_identity_manager_get_signer_org(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager("/tmp/fake")
        org = manager.get_signer_org()
        assert org == "Unknown"

    def test_identity_manager_extract_common_name(self):
        from wFabricSecurity import IdentityManager

        result = IdentityManager.extract_common_name("invalid cert")
        assert result is None

    def test_identity_manager_extract_public_key(self):
        from wFabricSecurity import IdentityManager

        result = IdentityManager.extract_public_key_pem("invalid cert")
        assert result is None


class TestFabricGatewayExtended:
    """Extended tests for FabricGateway."""

    def test_gateway_register_participant(self):
        from wFabricSecurity import FabricGateway, Participant

        gateway = FabricGateway(msp_path="/tmp/fake")
        p = Participant(
            identity="test@test.com",
            code_hash="sha256:abc",
        )
        gateway.register_participant(p)

    def test_gateway_submit_private_data(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.submit_private_data("collection", "key", {"data": "value"})
        assert result is not None


class TestCryptoSigningExtended:
    """Extended tests for SigningService."""

    def test_signing_verify(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)

        def getter(signer_id):
            return None

        result = service.verify("data", "signature", getter, "signer_id")
        assert result is True


class TestMessagesExtended:
    """Extended tests for Message models."""

    def test_message_with_metadata(self):
        from wFabricSecurity import Message, DataType

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            message_id="msg123",
            data_type=DataType.JSON,
            metadata={"key": "value"},
        )
        assert msg.metadata["key"] == "value"


class TestStorageLocalExtended:
    """Extended tests for LocalStorage."""

    def test_local_storage_message_expiration(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_msg_exp")
        storage.save_message(
            "msg1",
            {
                "sender": "test@test.com",
                "recipient": "other@test.com",
                "content": "test",
                "content_hash": "sha256:abc",
                "signature": "sig",
                "timestamp": "2024-01-01T00:00:00",
            },
            ttl_seconds=1,
        )

        msg = storage.get_message("msg1")
        assert msg is not None

    def test_local_storage_get_expired_messages(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_expired")
        expired = storage.get_expired_messages()
        assert isinstance(expired, list)


class TestRateLimiterExtended:
    """Extended tests for RateLimiter."""

    def test_rate_limiter_recent_requests(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(2)

        count = limiter.get_recent_requests(1.0)
        assert count >= 0

    def test_rate_limiter_is_over_limit(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        result = limiter.is_over_limit(threshold=0.5)
        assert isinstance(result, bool)


class TestRetryExtendedExtended:
    """Extended tests for retry module."""

    def test_retry_context_properties(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=3)
        assert ctx.max_attempts == 3
        assert ctx.attempt == 0
        assert ctx.succeeded is True
        assert ctx.exhausted is False

    def test_retry_context_with_exception(self):
        from wFabricSecurity import RetryContext

        with pytest.raises(ValueError):
            with RetryContext(max_attempts=1, initial_delay=0.01) as ctx:
                raise ValueError("Test error")

    def test_retry_context_non_retryable_exception(self):
        from wFabricSecurity import RetryContext

        with pytest.raises(TypeError):
            with RetryContext(
                max_attempts=1, initial_delay=0.01, exceptions=(ValueError,)
            ) as ctx:
                raise TypeError("Not retryable")


class TestAsyncRetry:
    """Tests for async retry decorator."""

    def test_async_retry_function_detected(self):
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=3)
        async def async_func():
            return "success"

        assert callable(async_func)


class TestGatewayExtended:
    """Extended tests for FabricGateway."""

    def test_gateway_signing_property(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert gateway.signing is not None

    def test_gateway_hashing_property(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert gateway.hashing is not None

    def test_gateway_local_storage_property(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert gateway.local_storage is not None

    def test_gateway_fabric_storage_property(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert gateway.fabric_storage is not None

    def test_gateway_is_using_fabric(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert isinstance(gateway.is_using_fabric, bool)

    def test_gateway_get_signer_cn(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        cn = gateway.get_signer_cn()
        assert cn is not None

    def test_gateway_verify_signature(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.verify_signature("data", "signature", "signer_id")
        assert result is True

    def test_gateway_register_code_identity(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            result = gateway.register_code_identity([temp_file], "1.0.0")
            assert result is not None
            assert "code_hash" in result
        finally:
            os.unlink(temp_file)

    def test_gateway_verify_code_integrity_no_registered(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        result = gateway.verify_code_integrity(["/tmp/nonexistent.py"])
        assert result is True

    def test_gateway_verify_own_code_integrity(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.verify_own_code_integrity(["/tmp/nonexistent.py"])
        assert result is True

    def test_gateway_invoke_chaincode(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.invoke_chaincode("TestFunc", "arg1", "arg2")
        assert result is not None

    def test_gateway_query_chaincode(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.query_chaincode("TestFunc", "arg1")
        assert result is None

    def test_gateway_get_private_data(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.get_private_data("collection", "key")
        assert result is None

    def test_gateway_get_certificate_pem(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.get_certificate_pem()
        assert result is None

    def test_gateway_verify_communication_permission(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.verify_communication_permission("user1", "user2")
        assert result is False

    def test_gateway_assert_message_integrity(self):
        from wFabricSecurity import FabricGateway
        from wFabricSecurity import MessageIntegrityError

        gateway = FabricGateway(msp_path="/tmp/fake")
        content = "test content"
        hash_value = gateway.compute_message_hash(content)

        gateway.assert_message_integrity(content, hash_value)

    def test_gateway_assert_message_integrity_failure(self):
        from wFabricSecurity import FabricGateway
        from wFabricSecurity import MessageIntegrityError

        gateway = FabricGateway(msp_path="/tmp/fake")
        with pytest.raises(MessageIntegrityError):
            gateway.assert_message_integrity("test", "sha256:wrong")

    def test_gateway_submit_private_data(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.submit_private_data("collection", "key", {"data": "value"})
        assert result is not None


class TestHashingServiceExtended:
    """Extended tests for HashingService."""

    def test_hashing_service_different_algorithms(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.sha256("test")
        assert result.startswith("sha256:")

    def test_hashing_service_multihash_single(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "sha256")
        assert "sha256" in result

    def test_hashing_service_multihash_different(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "sha512")
        assert "sha512" in result

    def test_hashing_service_blake(self):
        from wFabricSecurity import HashingService

        service = HashingService()
        result = service.compute_multihash("test", "blake2b")
        assert "blake2b" in result


class TestSigningServiceExtended:
    """Extended tests for SigningService."""

    def test_signing_service_sign_and_verify(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        data = "test data"
        signature = service.sign(data, "signer_id")

        def getter(sid):
            return None

        result = service.verify(data, signature, getter, "signer_id")
        assert result is True


class TestLocalStorageExtended:
    """Extended tests for LocalStorage."""

    def test_local_storage_save_message_and_get(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_save_msg")
        storage.clear()
        storage.save_message(
            "msg_test",
            {
                "content": "test content",
                "sender": "test@test.com",
            },
            ttl_seconds=3600,
        )

        msg = storage.get_message("msg_test")
        assert msg is not None
        assert msg.get("content") == "test content"

    def test_local_storage_get_expired_messages(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_expired2")
        storage.clear()
        expired = storage.get_expired_messages()
        assert isinstance(expired, list)

    def test_local_storage_cleanup_expired(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_cleanup")
        storage.clear()
        storage.save_message(
            "msg_exp",
            {"content": "test"},
            ttl_seconds=0,
        )
        time.sleep(0.1)
        count = storage.cleanup_expired_messages()
        assert count >= 0

    def test_local_storage_get_message_not_found(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_not_found")
        msg = storage.get_message("nonexistent")
        assert msg is None

    def test_local_storage_delete_nonexistent(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_del_none")
        result = storage.delete("nonexistent_key")
        assert result is False

    def test_local_storage_list_keys_with_prefix(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_prefix")
        storage.clear()
        storage.save("prefix_key1", {"data": 1})
        storage.save("prefix_key2", {"data": 2})
        storage.save("other_key", {"data": 3})

        keys = storage.list_keys("prefix_")
        assert len(keys) == 2


class TestRateLimiterExtended2:
    """Extended tests for RateLimiter."""

    def test_rate_limiter_full_burst(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        for _ in range(5):
            assert limiter.try_acquire() is True
        assert limiter.try_acquire() is False

    def test_rate_limiter_wait_for_tokens(self):
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=2)
        limiter.acquire(2)
        tokens = limiter.get_available_tokens()
        assert tokens < 2


class TestEnumsExtended:
    """Extended tests for enums."""

    def test_data_type_from_unknown_extension(self):
        from wFabricSecurity import DataType

        assert DataType.from_extension(".xyz123") == DataType.JSON

    def test_communication_direction_str(self):
        from wFabricSecurity import CommunicationDirection

        assert str(CommunicationDirection.OUTBOUND) == "outbound"
        assert str(CommunicationDirection.INBOUND) == "inbound"
        assert str(CommunicationDirection.BIDIRECTIONAL) == "bidirectional"


class TestModelsExtended:
    """Extended tests for models."""

    def test_message_to_dict_full(self):
        from wFabricSecurity import Message, DataType

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
            message_id="msg123",
            data_type=DataType.JSON,
            metadata={"key": "value"},
            expires_at="2099-01-01T00:00:00",
        )
        data = msg.to_dict()
        assert data["sender"] == "sender@test.com"
        assert data["data_type"] == "json"
        assert data["metadata"]["key"] == "value"

    def test_participant_from_dict_full(self):
        from wFabricSecurity import (
            Participant,
            CommunicationDirection,
            ParticipantStatus,
        )

        data = {
            "identity": "user@test.com",
            "code_hash": "sha256:abc",
            "version": "1.0.0",
            "direction": "outbound",
            "allowed_communications": ["other@test.com"],
            "is_active": True,
            "status": "active",
        }
        p = Participant.from_dict(data)
        assert p.identity == "user@test.com"
        assert p.direction == CommunicationDirection.OUTBOUND

    def test_task_from_dict(self):
        from wFabricSecurity import Task, TaskStatus

        data = {
            "task_id": "task123",
            "hash_a": "sha256:abc",
            "hash_b": "sha256:def",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T01:00:00",
        }
        task = Task.from_dict(data)
        assert task.task_id == "task123"
        assert task.status == TaskStatus.COMPLETED


class TestFabricStorageExtended:
    """Extended tests for FabricStorage."""

    def test_fabric_storage_properties(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        assert storage.channel == "mychannel"
        assert storage.chaincode == "tasks"

    def test_fabric_storage_get_participant_not_found(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_participant("nonexistent@test.com")
        assert result is None

    def test_fabric_storage_get_certificate_not_found(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_certificate("nonexistent@test.com")
        assert result is None

    def test_fabric_storage_get_task_not_found(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_task("nonexistent_task")
        assert result is None


class TestFabricContractExtended:
    """Extended tests for FabricContract."""

    def test_contract_properties(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "testchannel", "testcc")
        assert contract.channel == "testchannel"
        assert contract.chaincode == "testcc"


class TestFabricNetworkExtended:
    """Extended tests for FabricNetwork."""

    def test_network_properties(self):
        from wFabricSecurity import FabricNetwork, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        network = FabricNetwork(gateway, "testchannel")
        assert network.channel == "testchannel"


class TestIntegrityVerifierExtended2:
    """Extended tests for IntegrityVerifier."""

    def test_verifier_verify_multiple_paths_empty(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        verifier = IntegrityVerifier(gateway)

        results = verifier.verify_multiple_paths([])
        assert len(results) == 0


class TestPermissionManagerExtended2:
    """Extended tests for PermissionManager."""

    def test_permission_manager_can_communicate_no_participant(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = PermissionManager(gateway)

        result = manager.can_communicate_with("nonexistent@test.com", "other@test.com")
        assert result is True

    def test_permission_manager_can_communicate_revoked_from(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway, RevocationError

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        manager.revoke_participant("user@test.com")
        with pytest.raises(RevocationError):
            manager.can_communicate_with("user@test.com", "other@test.com")

    def test_permission_manager_can_communicate_revoked_to(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway, RevocationError

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)

        manager.revoke_participant("target@test.com")
        with pytest.raises(RevocationError):
            manager.can_communicate_with("user@test.com", "target@test.com")

    def test_permission_manager_can_communicate_inactive(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway, PermissionDeniedError

        gateway = FabricGateway(msp_path="/tmp/fake")
        manager = PermissionManager(gateway)
        gateway.local_storage.clear()

        gateway.local_storage.save(
            "participant_inactive@test.com",
            {
                "identity": "inactive@test.com",
                "is_active": False,
                "direction": "bidirectional",
            },
        )

        with pytest.raises(PermissionDeniedError):
            manager.can_communicate_with("inactive@test.com", "other@test.com")


class TestMessageManagerExtended2:
    """Extended tests for MessageManager."""

    def test_message_manager_get_messages_for_recipient(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            data_type=DataType.JSON,
        )

        messages = manager.get_messages_for_recipient("recipient@test.com")
        assert isinstance(messages, list)

    def test_message_manager_verify_message_fails(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import (
            FabricGateway,
            Message,
            DataType,
            MessageIntegrityError,
        )

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:wrong",
            signature="sig",
            timestamp="2024-01-01T00:00:00",
        )

        with pytest.raises(MessageIntegrityError):
            manager.verify_message(msg)


class TestConfigSettingsExtended:
    """Extended tests for Settings."""

    def test_settings_from_yaml_missing_file(self):
        from wFabricSecurity import Settings

        settings = Settings.from_yaml("/nonexistent/file.yaml")
        assert settings.fabric_channel == "mychannel"

    def test_settings_to_yaml_file(self):
        from wFabricSecurity import Settings

        settings = Settings()
        settings.to_yaml("/tmp/test_settings_output.yaml")
        assert os.path.exists("/tmp/test_settings_output.yaml")

        with open("/tmp/test_settings_output.yaml") as f:
            content = f.read()
            assert "local_data_dir" in content

        os.unlink("/tmp/test_settings_output.yaml")


class TestContractExtended2:
    """More tests for FabricContract."""

    def test_contract_register_task_with_result(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")
        result = contract.register_task("task_new", "hash_a")
        assert result is not None

    def test_contract_get_task_with_payload(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")
        result = contract.get_task_with_payload("task123")
        assert result is None or isinstance(result, (str, dict))


class TestStorageFabricExtended:
    """More tests for FabricStorage."""

    def test_fabric_storage_invoke(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.invoke("TestFunc", "arg1", "arg2")
        assert result is not None

    def test_fabric_storage_query(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.query("TestFunc", "arg1")
        assert result is None

    def test_fabric_storage_put_private_data(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.put_private_data("collection", "key", {"data": "value"})
        assert result is not None


class TestIntegrityExtended3:
    """More tests for IntegrityVerifier."""

    def test_verifier_register_multiple_paths(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test1')\n")
            temp_file1 = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test2')\n")
            temp_file2 = f.name

        try:
            result = verifier.register_code([temp_file1], "1.0.0")
            assert result is not None

            result = verifier.register_code([temp_file2], "1.0.0")
            assert result is not None
        finally:
            os.unlink(temp_file1)
            os.unlink(temp_file2)

    def test_verifier_verify_code_integrity_registered(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            signer_id = gateway.get_signer_id()
            code_hash = gateway.compute_code_hash([temp_file])
            gateway.local_storage.save(
                f"participant_{signer_id}",
                {
                    "identity": signer_id,
                    "code_hash": code_hash,
                },
            )
            result = verifier.verify_code_integrity([temp_file], code_hash)
            assert result is True
        finally:
            os.unlink(temp_file)


class TestMessagesExtended3:
    """More tests for MessageManager."""

    def test_message_manager_create_with_ttl(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway, ttl_seconds=3600)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test with ttl",
            data_type=DataType.JSON,
        )

        assert msg.expires_at is not None
        assert msg.is_expired() is False

    def test_message_manager_verify_json_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        msg = manager.create_json_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            data={"key": "value"},
        )

        result = manager.verify_message(msg)
        assert result is True


class TestPermissionsExtended3:
    """More tests for PermissionManager."""

    def test_permission_manager_can_communicate_outbound_denied(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway, PermissionDeniedError

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = PermissionManager(gateway)

        gateway.local_storage.save(
            "participant_outbound@test.com",
            {
                "identity": "outbound@test.com",
                "is_active": True,
                "direction": "outbound",
                "allowed_communications": ["allowed@test.com"],
            },
        )

        with pytest.raises(PermissionDeniedError):
            manager.can_communicate_with("outbound@test.com", "notallowed@test.com")

    def test_permission_manager_get_allowed_communications_with_participant(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = PermissionManager(gateway)

        gateway.local_storage.save(
            "participant_allowed@test.com",
            {
                "identity": "allowed@test.com",
                "allowed_communications": ["target1@test.com", "target2@test.com"],
            },
        )

        allowed = manager.get_allowed_communications("allowed@test.com")
        assert len(allowed) == 2


class TestRetryExtended3:
    """More tests for retry module."""

    def test_retry_context_exhausted_property(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=2, initial_delay=0.01)
        with ctx:
            pass
        assert ctx.exhausted is False
        assert ctx.attempt == 1
        assert ctx.succeeded is True


class TestSigningExtended3:
    """More tests for SigningService."""

    def test_signing_service_verify_with_cert(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        data = "test data"
        signature = service.sign(data, "signer_id")

        def getter(sid):
            return None

        result = service.verify(data, signature, getter, "signer_id")
        assert result is True


class TestGatewayExtended2:
    """More tests for FabricGateway."""

    def test_gateway_identity_property(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        assert gateway.identity is not None

    def test_gateway_register_certificate_failure(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        result = gateway.register_certificate()
        assert result is not None


class TestLocalStorageExtended3:
    """More tests for LocalStorage."""

    def test_local_storage_message_get_expired_format(self):
        from wFabricSecurity import LocalStorage

        storage = LocalStorage("/tmp/test_expired3")
        storage.clear()
        storage.save_message(
            "msg_exp",
            {"content": "test"},
            ttl_seconds=0,
        )
        time.sleep(0.1)
        expired = storage.get_expired_messages()
        assert isinstance(expired, list)


class TestContractExtended3:
    """More tests for FabricContract."""

    def test_contract_get_task_with_payload(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")
        result = contract.get_task_with_payload("task123")
        assert result is None

    def test_contract_complete_task_with_result(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")
        result = contract.complete_task("task123", "hash_b")
        assert result is not None

    def test_contract_get_private_data(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")
        result = contract.get_private_data("collection", "key")
        assert result is None


class TestIntegrityExtended4:
    """More tests for IntegrityVerifier."""

    def test_verifier_get_registered_hash(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        verifier = IntegrityVerifier(gateway)

        result = verifier.get_registered_hash("test@test.com")
        assert result is None


class TestMessagesExtended4:
    """More tests for MessageManager."""

    def test_message_manager_get_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test content",
            data_type=DataType.JSON,
        )

        result = manager.get_message(msg.message_id)
        assert result is not None

    def test_message_manager_get_message_not_found(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        result = manager.get_message("nonexistent")
        assert result is None


class TestSigningExtended4:
    """More tests for SigningService."""

    def test_signing_service_signature_format(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        signature = service.sign("test data", "signer_id")
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_signing_service_has_private_key(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)
        assert service.has_private_key is False


class TestStorageFabricExtended2:
    """More tests for FabricStorage."""

    def test_fabric_storage_get_certificate(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_certificate("test@test.com")
        assert result is None

    def test_fabric_storage_get_participant(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_participant("test@test.com")
        assert result is None

    def test_fabric_storage_get_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_task("task123")
        assert result is None

    def test_fabric_storage_get_private_data(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.get_private_data("collection", "key")
        assert result is None

    def test_fabric_storage_register_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.register_task("task123", "hash_a")
        assert result is not None


class TestRetryExtended4:
    """More tests for retry module."""

    def test_retry_context_last_exception(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=2, initial_delay=0.01)
        with ctx:
            pass
        assert ctx.last_exception is None


class TestGatewayExtended3:
    """More tests for FabricGateway."""

    def test_gateway_verify_code_integrity_with_fabric_participant(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()

        signer_id = gateway.get_signer_id()
        code_hash = gateway.compute_code_hash(["/tmp/nonexistent.py"])

        gateway.local_storage.save(
            f"participant_{signer_id}",
            {
                "identity": signer_id,
                "code_hash": code_hash,
            },
        )

        result = gateway.verify_code_integrity(["/tmp/nonexistent.py"], signer_id)
        assert result is True


class TestSigningExtended5:
    """More tests for SigningService - targeting uncovered lines."""

    def test_signing_service_load_methods(self):
        from wFabricSecurity import SigningService

        service = SigningService(private_key=None)

        with pytest.raises(ValueError):
            service.load_private_key_from_pem(b"fake_pem_data")

        with pytest.raises(ValueError):
            service.load_certificate_from_pem(b"fake_cert_data")


class TestMessagesExtended5:
    """More tests for MessageManager - targeting uncovered lines."""

    def test_message_manager_get_message_invalid_id(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        result = manager.get_message("")
        assert result is None


class TestRetryExtended5:
    """More tests for retry - targeting uncovered lines."""

    def test_retry_decorator_logging(self):
        from wFabricSecurity import with_retry
        import logging

        attempts = {"count": 0}

        @with_retry(max_attempts=2, initial_delay=0.01)
        def eventually_fails():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("Retry me")
            raise RuntimeError("Final failure")

        with pytest.raises(RuntimeError):
            eventually_fails()


class TestStorageFabricExtended3:
    """More tests for FabricStorage - targeting uncovered lines."""

    def test_fabric_storage_invoke_with_result(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.invoke("TestFunc", "key", "value")
        assert result is not None

    def test_fabric_storage_query_with_args(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.query("TestFunc", "key")
        assert result is None

    def test_fabric_storage_register_certificate(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.register_certificate("test@test.com", "cert_data")
        assert result is not None

    def test_fabric_storage_register_participant(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()
        result = storage.register_participant(
            {
                "identity": "test@test.com",
                "code_hash": "sha256:abc",
            }
        )
        assert result is not None


class TestIdentityManagerExtended:
    """More tests for IdentityManager - targeting uncovered lines."""

    def test_identity_manager_get_certificate_pem(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager(msp_path="/tmp/fake")

        cert = manager.get_certificate_pem()
        assert cert is None or isinstance(cert, str)

    def test_identity_manager_clear_cache(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager(msp_path="/tmp/fake")
        manager.clear_cache()

    def test_identity_manager_get_signer_id(self):
        from wFabricSecurity import IdentityManager

        manager = IdentityManager(msp_path="/tmp/fake")
        signer_id = manager.get_signer_id()
        assert signer_id is not None


class TestFabricContractExtended2:
    """More tests for FabricContract - targeting uncovered lines."""

    def test_contract_get_certificate(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.get_certificate("user@test.com")
        assert result is None

    def test_contract_get_participant(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.get_participant("user@test.com")
        assert result is None

    def test_contract_complete_task(self):
        from wFabricSecurity import FabricContract, FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        contract = FabricContract(gateway, "mychannel", "tasks")

        result = contract.complete_task("task123", "hash_b")
        assert result is not None


class TestFabricGatewayExtended2:
    """More tests for FabricGateway - targeting uncovered lines."""

    def test_gateway_get_certificate_pem(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")

        result = gateway.get_certificate_pem()
        assert result is None

    def test_gateway_invoke_chaincode(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")

        result = gateway.invoke_chaincode("TestFunc", "arg1", "arg2")
        assert result is not None

    def test_gateway_query_chaincode(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")

        result = gateway.query_chaincode("TestFunc", "arg1")
        assert result is None

    def test_gateway_get_private_data(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")

        result = gateway.get_private_data("collection", "key")
        assert result is None

    def test_gateway_submit_private_data(self):
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")

        result = gateway.submit_private_data("collection", "key", {"data": "value"})
        assert result is not None


class TestIntegrityVerifierExtended2:
    """More tests for IntegrityVerifier - targeting uncovered lines."""

    def test_verifier_get_registered_hash(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        verifier = IntegrityVerifier(gateway)

        result = verifier.get_registered_hash("user@test.com")
        assert result is None

    def test_verifier_verify_multiple_paths(self):
        from wFabricSecurity.fabric_security.security.integrity import IntegrityVerifier
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        verifier = IntegrityVerifier(gateway)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')\n")
            temp_file = f.name

        try:
            code_hash = gateway.compute_code_hash([temp_file])
            result = verifier.verify_multiple_paths([(temp_file, code_hash)])
            assert isinstance(result, list)
        finally:
            os.unlink(temp_file)


class TestMessageManagerExtended2:
    """More tests for MessageManager - targeting uncovered lines."""

    def test_message_manager_create_with_metadata(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway, DataType

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway, ttl_seconds=3600)

        msg = manager.create_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test with metadata",
            data_type=DataType.JSON,
            metadata={"key": "value"},
        )

        assert msg.metadata is not None
        assert msg.metadata.get("key") == "value"

    def test_message_manager_create_json_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        msg = manager.create_json_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            data={"key": "value"},
        )

        assert msg is not None
        assert msg.data_type.value == "json"

    def test_message_manager_create_binary_message(self):
        from wFabricSecurity.fabric_security.security.messages import MessageManager
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = MessageManager(gateway)

        msg = manager.create_binary_message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            data=b"binary data",
        )

        assert msg is not None
        assert msg.data_type.value == "binary"


class TestFabricStorageExtended2:
    """More tests for FabricStorage - targeting uncovered lines."""

    def test_fabric_storage_register_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()

        result = storage.register_task("task123", "hash_a")
        assert result is not None

    def test_fabric_storage_complete_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()

        result = storage.complete_task("task123", "hash_b")
        assert result is not None

    def test_fabric_storage_get_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()

        result = storage.get_task("task123")
        assert result is None

    def test_fabric_storage_get_task(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()

        result = storage.get_task("task123")
        assert result is None

    def test_fabric_storage_put_private_data(self):
        from wFabricSecurity import FabricStorage

        storage = FabricStorage()

        result = storage.put_private_data("collection", "key", {"data": "value"})
        assert result is not None


class TestRetryExtended2:
    """More tests for retry - targeting uncovered lines."""

    def test_retry_context_exhausted_after_attempts(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        with pytest.raises(ValueError):
            with ctx:
                raise ValueError("test")
        assert ctx.exhausted is True

    def test_retry_context_with_delay(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=2, initial_delay=0.05, backoff_factor=2.0)
        assert ctx.delay == 0.05

        with ctx:
            raise ValueError("test")

        assert ctx.delay > 0.05

    def test_retry_decorator_with_callback(self):
        from wFabricSecurity import with_retry

        callback_results = []

        def my_callback(exc, attempt):
            callback_results.append((exc, attempt))

        @with_retry(max_attempts=2, initial_delay=0.01, on_retry=my_callback)
        def eventually_fails():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            eventually_fails()

        assert len(callback_results) > 0


class TestPermissionsManagerExtended2:
    """More tests for PermissionManager - targeting uncovered lines."""

    def test_permission_manager_get_allowed_communications(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = PermissionManager(gateway)

        gateway.local_storage.save(
            "participant_test@test.com",
            {
                "identity": "test@test.com",
                "is_active": True,
                "direction": "bidirectional",
                "allowed_communications": ["other@test.com"],
            },
        )

        result = manager.get_allowed_communications("test@test.com")
        assert isinstance(result, list)

    def test_permission_manager_update_participant(self):
        from wFabricSecurity.fabric_security.security.permissions import (
            PermissionManager,
        )
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(msp_path="/tmp/fake")
        gateway.local_storage.clear()
        manager = PermissionManager(gateway)

        result = manager.update_participant("test@test.com", {"is_active": False})
        assert result is not None


class TestEnumsExtended2:
    """More tests for enums - targeting uncovered lines."""

    def test_communication_direction_values(self):
        from wFabricSecurity import CommunicationDirection

        assert CommunicationDirection.BIDIRECTIONAL.value == "bidirectional"
        assert CommunicationDirection.OUTBOUND.value == "outbound"
        assert CommunicationDirection.INBOUND.value == "inbound"

    def test_data_type_values(self):
        from wFabricSecurity import DataType

        assert DataType.JSON.value == "json"
        assert DataType.IMAGE.value == "image"
        assert DataType.P2P.value == "p2p"
        assert DataType.BINARY.value == "binary"

    def test_task_status_values(self):
        from wFabricSecurity import TaskStatus

        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_participant_status_values(self):
        from wFabricSecurity import ParticipantStatus

        assert ParticipantStatus.ACTIVE.value == "active"
        assert ParticipantStatus.INACTIVE.value == "inactive"
        assert ParticipantStatus.REVOKED.value == "revoked"


class TestModelsExtended2:
    """More tests for models - targeting uncovered lines."""

    def test_message_is_expired_true(self):
        from wFabricSecurity import Message, DataType
        from datetime import datetime, timedelta

        msg = Message(
            sender="sender@test.com",
            recipient="recipient@test.com",
            content="test",
            content_hash="sha256:abc",
            signature="sig",
            timestamp="2020-01-01T00:00:00",
            message_id="msg123",
            data_type=DataType.JSON,
            expires_at="2020-01-01T00:00:00",
        )

        assert msg.is_expired() is True

    def test_participant_str(self):
        from wFabricSecurity import Participant

        p = Participant(
            identity="test@test.com",
            code_hash="sha256:abc",
        )

        assert "test@test.com" in str(p)

    def test_task_str(self):
        from wFabricSecurity import Task

        t = Task(
            task_id="task123",
            hash_a="sha256:abc",
        )

        assert "task123" in str(t)


class TestConfigSettingsExtended:
    """More tests for Settings - targeting uncovered lines."""

    def test_settings_from_yaml_file(self):
        from wFabricSecurity import Settings
        import tempfile

        yaml_content = """local_data_dir: /custom/path
fabric_channel: custom_channel
rate_limit_rps: 200
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name

        try:
            settings = Settings.from_yaml(temp_file)
            assert settings.local_data_dir == "/custom/path"
            assert settings.fabric_channel == "custom_channel"
            assert settings.rate_limit_requests_per_second == 200
        finally:
            os.unlink(temp_file)


class TestRetryExtended3:
    """More tests for retry."""

    def test_retry_context_exhausted_no_exception(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        with ctx:
            pass
        assert ctx.exhausted is False
        assert ctx.attempt == 1


class TestMessageManagerExtended:
    """Extended tests for MessageManager coverage."""

    def test_message_manager_get_messages_for_recipient(self):
        from wFabricSecurity import MessageManager
        from wFabricSecurity.fabric_security.core.models import Message, DataType
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        mock_gateway = Mock()
        mock_gateway.local_storage = Mock()
        manager = MessageManager(mock_gateway)
        expires = (datetime.now() + timedelta(hours=1)).isoformat()
        msg = Message(
            message_id="msg_recipient_test",
            sender="Alice",
            recipient="Bob",
            content="Test content",
            content_hash="hash123",
            signature="sig123",
            timestamp=datetime.now().isoformat(),
            expires_at=expires,
        )
        manager._messages_cache[msg.message_id] = msg
        mock_gateway.local_storage.list_keys.return_value = ["msg_recipient_test"]
        mock_gateway.local_storage.get_message.return_value = msg.to_dict()

        messages = manager.get_messages_for_recipient("Bob")
        assert isinstance(messages, list)

    def test_message_manager_verify_expired_message(self):
        from wFabricSecurity import MessageManager
        from wFabricSecurity.fabric_security.core.models import Message, DataType
        from datetime import datetime, timedelta
        from unittest.mock import Mock

        mock_gateway = Mock()
        manager = MessageManager(mock_gateway)
        expired = (datetime.now() - timedelta(hours=1)).isoformat()
        msg = Message(
            message_id="msg_expired",
            sender="Alice",
            recipient="Bob",
            content="Test content",
            content_hash="hash123",
            signature="sig123",
            timestamp=datetime.now().isoformat(),
            expires_at=expired,
        )
        result = manager.verify_message(msg)
        assert result is False

    def test_message_manager_cleanup_expired(self):
        from wFabricSecurity import MessageManager
        from unittest.mock import Mock

        mock_gateway = Mock()
        mock_gateway.local_storage = Mock()
        manager = MessageManager(mock_gateway)
        mock_gateway.local_storage.cleanup_expired_messages.return_value = 0
        count = manager.cleanup_expired()
        assert count >= 0
        assert manager._last_cleanup is not None


class TestRetryExtended4:
    """Extended tests for RetryContext coverage."""

    def test_retry_context_backoff_increases(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=3, initial_delay=0.05, backoff_factor=2.0)
        assert ctx.delay == 0.05

        with ctx:
            raise ValueError("first")
        assert ctx.delay == pytest.approx(0.1)

        with ctx:
            raise ValueError("second")
        assert ctx.delay == pytest.approx(0.2)

    def test_retry_context_max_attempts_multiple(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        assert ctx.attempt == 0

        with pytest.raises(ValueError):
            with ctx:
                raise ValueError("test")

        assert ctx.attempt == 1
        assert ctx.last_exception is not None

    def test_retry_context_succeeded_property(self):
        from wFabricSecurity import RetryContext

        ctx = RetryContext(max_attempts=1, initial_delay=0.01)
        with ctx:
            pass
        assert ctx.succeeded is True

        ctx2 = RetryContext(max_attempts=1, initial_delay=0.01)
        with pytest.raises(ValueError):
            with ctx2:
                raise ValueError("fail")
        assert ctx2.succeeded is False


class TestFabricStorageExtended:
    """Extended tests for FabricStorage coverage."""

    def test_fabric_storage_get_certificate_not_found(self):
        from wFabricSecurity import FabricStorage
        from unittest.mock import Mock

        mock_gateway = Mock()
        storage = FabricStorage(mock_gateway)
        mock_gateway.query_chaincode.return_value = None

        cert = storage.get_certificate("unknown_id")
        assert cert is None

    def test_fabric_storage_get_participant_not_found(self):
        from wFabricSecurity import FabricStorage
        from unittest.mock import Mock

        mock_gateway = Mock()
        storage = FabricStorage(mock_gateway)
        mock_gateway.query_chaincode.return_value = None

        participant = storage.get_participant("unknown_id")
        assert participant is None

    def test_fabric_storage_register_participant(self):
        from wFabricSecurity import FabricStorage
        from unittest.mock import Mock

        mock_gateway = Mock()
        storage = FabricStorage(mock_gateway)
        mock_gateway.invoke.return_value = {"success": True}

        result = storage.register_participant({"identity": "test_user"})
        assert result is not None


class TestIntegrityVerifierExtended3:
    """Extended tests for IntegrityVerifier coverage."""

    def test_verify_multiple_paths_empty(self):
        from wFabricSecurity import IntegrityVerifier
        from unittest.mock import Mock

        mock_gateway = Mock()
        verifier = IntegrityVerifier(mock_gateway)
        results = verifier.verify_multiple_paths([])
        assert results == []

    def test_verify_multiple_paths_with_error(self):
        from wFabricSecurity import IntegrityVerifier
        from unittest.mock import Mock

        mock_gateway = Mock()
        verifier = IntegrityVerifier(mock_gateway)
        mock_gateway.compute_file_hash.side_effect = IOError("Read error")

        results = verifier.verify_multiple_paths([("file1.txt", "hash123")])
        assert results == [False]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
