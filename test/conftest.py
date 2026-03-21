"""
Test suite configuration and shared fixtures for wFabricSecurity
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock

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


@pytest.fixture
def mock_gateway():
    """Create a mock FabricGateway for testing."""
    gateway = Mock()
    gateway.msp_path = "/tmp/fake"
    gateway.channel = "test-channel"
    gateway.chaincode = "test-cc"

    gateway.local_storage = Mock()
    gateway.local_storage.list_keys.return_value = []
    gateway.local_storage.get_message.return_value = None

    gateway.query_chaincode.return_value = {"result": "success"}
    gateway.invoke_chaincode.return_value = {"success": True}
    gateway.compute_message_hash.return_value = "hash123"
    gateway.compute_file_hash.return_value = "file_hash"
    gateway.verify_signature.return_value = True
    gateway.get_certificate_pem.return_value = "CERT_PEM"
    gateway.get_signer_cn.return_value = "TestUser"
    gateway.get_signer_id.return_value = "TestUser"
    gateway.is_using_fabric.return_value = False

    return gateway


@pytest.fixture
def mock_contract():
    """Create a mock FabricContract for testing."""
    contract = Mock()
    contract.get_participant.return_value = {"identity": "TestUser"}
    contract.get_certificate.return_value = "CERT"
    contract.complete_task.return_value = {"success": True}
    return contract
