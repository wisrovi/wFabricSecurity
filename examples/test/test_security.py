"""
Tests for wFabricSecurity - Security Module (Rate Limiting, Retry, etc.)
"""

import os
import sys
import pytest
import time

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_rate_limiter_init(self):
        """Test RateLimiter initialization."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=20)
        assert limiter.requests_per_second == 10
        assert limiter.burst_size == 20

    def test_rate_limiter_acquire(self):
        """Test RateLimiter.acquire()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=10)
        assert limiter.acquire(tokens=1) is True

    def test_rate_limiter_try_acquire(self):
        """Test RateLimiter.try_acquire()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=100, burst=1)
        assert limiter.try_acquire() is True
        assert limiter.try_acquire() is False

    def test_rate_limiter_available_tokens(self):
        """Test RateLimiter.get_available_tokens()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        tokens = limiter.get_available_tokens()
        assert tokens == 5

        limiter.acquire(3)
        tokens = limiter.get_available_tokens()
        assert tokens < 5

    def test_rate_limiter_stats(self):
        """Test RateLimiter.get_stats()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(2)

        stats = limiter.get_stats()
        assert "available_tokens" in stats
        assert "requests_per_second" in stats
        assert "recent_requests_1s" in stats

    def test_rate_limiter_block_unblock(self):
        """Test RateLimiter.block_for() and unblock()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        assert limiter.is_blocked is False

        limiter.block_for(1)
        assert limiter.is_blocked is True

        time.sleep(1.1)
        assert limiter.is_blocked is False

    def test_rate_limiter_reset(self):
        """Test RateLimiter.reset()."""
        from wFabricSecurity import RateLimiter

        limiter = RateLimiter(requests_per_second=10, burst=5)
        limiter.acquire(3)
        limiter.reset()

        stats = limiter.get_stats()
        assert stats["available_tokens"] == 5


class TestRetry:
    """Tests for retry decorator."""

    def test_retry_success(self):
        """Test @with_retry with successful function."""
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=3)
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_retry_eventual_success(self):
        """Test @with_retry with eventual success."""
        from wFabricSecurity import with_retry

        attempts = {"count": 0}

        @with_retry(max_attempts=3, initial_delay=0.01, backoff_factor=1.0)
        def eventually_successful():
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("Not yet")
            return "success"

        result = eventually_successful()
        assert result == "success"
        assert attempts["count"] == 2

    def test_retry_exhausted(self):
        """Test @with_retry with exhausted attempts."""
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_retry_specific_exceptions(self):
        """Test @with_retry with specific exceptions."""
        from wFabricSecurity import with_retry

        @with_retry(max_attempts=2, exceptions=(ValueError,), initial_delay=0.01)
        def fails_with_value_error():
            raise ValueError("Value error")

        @with_retry(max_attempts=2, exceptions=(ValueError,), initial_delay=0.01)
        def fails_with_type_error():
            raise TypeError("Type error")

        with pytest.raises(ValueError):
            fails_with_value_error()

        with pytest.raises(TypeError):
            fails_with_type_error()

    def test_retry_context(self):
        """Test RetryContext."""
        from wFabricSecurity.security.retry import RetryContext

        with RetryContext(max_attempts=3) as ctx:
            pass
        assert ctx.succeeded is True
        assert ctx.attempt == 1


class TestLocalStorage:
    """Tests for LocalStorage."""

    def test_local_storage_init(self):
        """Test LocalStorage initialization."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_storage")
        assert storage._data_dir.name == "test_fabric_storage"

    def test_local_storage_save_get(self):
        """Test LocalStorage.save() and get()."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_save")
        storage.save("test_key", {"data": "value"})

        result = storage.get("test_key")
        assert result["data"] == "value"

    def test_local_storage_delete(self):
        """Test LocalStorage.delete()."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_delete")
        storage.save("delete_key", {"data": "value"})

        assert storage.delete("delete_key") is True
        assert storage.exists("delete_key") is False

    def test_local_storage_list_keys(self):
        """Test LocalStorage.list_keys()."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_list")
        storage.save("key1", {"data": 1})
        storage.save("key2", {"data": 2})
        storage.save("prefix_key", {"data": 3})

        keys = storage.list_keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_local_storage_revoked_participants(self):
        """Test LocalStorage revocation methods."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_revoked")
        storage.add_revoked_participant("user@test.com")

        assert storage.is_participant_revoked("user@test.com") is True
        assert storage.is_participant_revoked("other@test.com") is False

        revoked = storage.get_revoked_participants()
        assert "user@test.com" in revoked

    def test_local_storage_stats(self):
        """Test LocalStorage.get_stats()."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_stats")
        storage.save("key1", {"data": "value"})

        stats = storage.get_stats()
        assert "total_keys" in stats
        assert "size_bytes" in stats

    def test_local_storage_clear(self):
        """Test LocalStorage.clear()."""
        from wFabricSecurity.storage import LocalStorage

        storage = LocalStorage("/tmp/test_fabric_clear")
        storage.save("key1", {"data": "value"})
        storage.save("key2", {"data": "value"})

        storage.clear()
        assert storage.list_keys() == []


class TestIdentityManager:
    """Tests for IdentityManager."""

    def test_identity_manager_init(self):
        """Test IdentityManager initialization."""
        from wFabricSecurity.crypto import IdentityManager

        msp_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "enviroment",
            "organizations",
            "peerOrganizations",
            "org1.net",
            "users",
            "Admin@org1.net",
            "msp",
        )

        manager = IdentityManager(msp_path)
        assert manager.msp_path == msp_path

    def test_identity_manager_cache(self):
        """Test IdentityManager certificate caching."""
        from wFabricSecurity.crypto import IdentityManager

        manager = IdentityManager("/tmp/fake_path")
        manager.cache_certificate("user@test.com", "cert_pem_data")

        cached = manager.get_cached_certificate("user@test.com")
        assert cached == "cert_pem_data"

    def test_identity_manager_cache_expired(self):
        """Test IdentityManager cache expiration."""
        from wFabricSecurity.crypto import IdentityManager
        import time

        manager = IdentityManager("/tmp/fake_path", cache_ttl_seconds=1)
        manager.cache_certificate("user@test.com", "cert_pem_data")

        time.sleep(1.5)
        cached = manager.get_cached_certificate("user@test.com")
        assert cached is None


class TestFabricGateway:
    """Tests for FabricGateway."""

    def test_gateway_init(self):
        """Test FabricGateway initialization."""
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(
            peer_url="localhost:7051",
            msp_path="/tmp/fake_msp",
        )
        assert gateway.peer_url == "localhost:7051"

    def test_gateway_hash(self):
        """Test FabricGateway hashing methods."""
        from wFabricSecurity import FabricGateway

        gateway = FabricGateway(
            peer_url="localhost:7051",
            msp_path="/tmp/fake_msp",
        )

        code_hash = gateway.compute_code_hash(["/tmp/fake_file.py"])
        assert code_hash.startswith("sha256:")

        msg_hash = gateway.compute_message_hash("test content")
        assert msg_hash.startswith("sha256:")


class TestFabricSecurity:
    """Tests for FabricSecurity main class."""

    def test_fabric_security_init(self):
        """Test FabricSecurity initialization."""
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
        """Test FabricSecurity rate limiter integration."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(
            me="TestUser", rate_limit_rps=100, rate_limit_burst=10
        )

        assert security.rate_limiter.try_acquire() is True
        stats = security.rate_limiter.get_stats()
        assert stats["requests_per_second"] == 100

    def test_fabric_security_stats(self):
        """Test FabricSecurity.get_stats()."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser")
        stats = security.get_stats()

        assert "identity" in stats
        assert "using_fabric" in stats
        assert "rate_limiter" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
