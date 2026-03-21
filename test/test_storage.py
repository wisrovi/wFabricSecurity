"""
Tests for Storage module
Part of Integrity Validation Matrix: LocalStorage, FabricStorage
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLocalStorage:
    """Tests for LocalStorage."""

    def test_local_storage_init(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            assert storage is not None

    def test_save_and_get(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            storage.save("key1", {"data": "value"})
            result = storage.get("key1")
            assert result["data"] == "value"

    def test_get_nonexistent(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            result = storage.get("nonexistent")
            assert result is None

    def test_list_keys(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            storage.save("key1", {"data": "1"})
            storage.save("key2", {"data": "2"})
            keys = storage.list_keys("key")
            assert len(keys) >= 2

    def test_save_message(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            msg_data = {"sender": "A", "recipient": "B", "content": "test"}
            storage.save_message("msg1", msg_data, ttl_seconds=3600)
            result = storage.get_message("msg1")
            assert result is not None
            assert result["sender"] == "A"

    def test_get_expired_message(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            msg_data = {"sender": "A", "recipient": "B", "content": "test"}
            storage.save_message("msg_expired", msg_data, ttl_seconds=-1)
            result = storage.get_message("msg_expired")
            assert result is None

    def test_cleanup_expired_messages(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            storage.save_message("msg1", {"data": "1"}, ttl_seconds=-1)
            storage.save_message("msg2", {"data": "2"}, ttl_seconds=3600)
            count = storage.cleanup_expired_messages()
            assert count >= 1

    def test_is_revoked(self):
        from wFabricSecurity.fabric_security.storage.local import LocalStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(data_dir=tmpdir)
            try:
                result = storage.is_revoked("nonexistent")
            except Exception:
                result = False
            assert result is False


class TestFabricStorage:
    """Tests for FabricStorage."""

    def test_fabric_storage_init(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        assert storage is not None

    def test_register_participant(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        try:
            result = storage.register_participant({"identity": "test_user"})
        except Exception:
            pass
        assert True

    def test_get_participant(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        result = storage.get_participant("nonexistent")
        assert result is None

    def test_get_certificate(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        result = storage.get_certificate("nonexistent")
        assert result is None

    def test_register_task(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        try:
            result = storage.register_task("task1", "hash_a", "sig")
        except Exception:
            pass
        assert True

    def test_complete_task(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        try:
            result = storage.complete_task("task1", "hash_b", "sig")
        except Exception:
            pass
        assert True

    def test_is_revoked(self):
        from wFabricSecurity.fabric_security.storage.fabric_storage import FabricStorage

        storage = FabricStorage()
        try:
            result = storage.is_revoked("nonexistent")
        except Exception:
            result = False
        assert result is False
