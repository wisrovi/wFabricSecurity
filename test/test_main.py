"""
Main test file for wFabricSecurity library
This file runs all test modules
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVersion:
    """Tests for version information."""

    def test_version_exists(self):
        from wFabricSecurity import __version__

        assert __version__ is not None

    def test_version_format(self):
        from wFabricSecurity import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2


class TestMainClasses:
    """Tests for main classes."""

    def test_fabric_security_import(self):
        from wFabricSecurity import FabricSecurity

        assert FabricSecurity is not None

    def test_fabric_security_simple_import(self):
        from wFabricSecurity import FabricSecuritySimple

        assert FabricSecuritySimple is not None

    def test_fabric_security_init(self):
        from wFabricSecurity import FabricSecurity

        fs = FabricSecurity(me="TestUser", msp_path="/tmp/fake")
        assert fs.me == "TestUser"

    def test_fabric_security_simple_init(self):
        from wFabricSecurity import FabricSecuritySimple

        fss = FabricSecuritySimple(me="TestUser")
        assert fss.me == "TestUser"


class TestSecurityDecorators:
    """Tests for security decorators."""

    def test_decorators_exist(self):
        from wFabricSecurity.fabric_security.security.decorators import (
            master_audit,
            slave_verify,
        )

        assert master_audit is not None
        assert slave_verify is not None
