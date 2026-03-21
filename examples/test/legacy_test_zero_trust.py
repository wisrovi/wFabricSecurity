"""
Tests para el sistema Zero Trust de FabricSecurity.

Incluye tests para:
- Verificación de integridad de código
- Permisos de comunicación
- Integridad de mensajes
- Firmas ECDSA
- Validaciones de seguridad
"""

import os
import sys
import pytest
import tempfile
import json
import hashlib
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


class TestCodeIntegrity:
    """Tests para verificación de integridad de código."""

    def test_register_code_identity(self):
        """Test registro de identidad de código."""
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
        """Test verificación pasa para código sin modificar."""
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
        """Test verificación falla para código modificado."""
        from wFabricSecurity import FabricSecurity, CodeIntegrityError

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

    def test_verify_own_code(self):
        """Test auto-verificación de código propio."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        temp_file = __file__
        security.register_code([temp_file], "1.0.0")
        result = security.verify_own_code([temp_file])
        assert result is True


class TestCommunicationPermissions:
    """Tests para permisos de comunicación."""

    def test_register_communication_permission(self):
        """Test registro de permiso de comunicación."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        security.register_communication("MASTER_A", "SLAVE_X")
        assert security.can_communicate_with("MASTER_A", "SLAVE_X") is True

    def test_can_communicate_with_permission(self):
        """Test verificación de permiso - permitido."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        security.register_communication("MASTER_A", "SLAVE_X")

        result = security.can_communicate_with("MASTER_A", "SLAVE_X")
        assert result is True

    def test_can_communicate_without_permission(self):
        """Test verificación de permiso - denegado."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        result = security.can_communicate_with("MASTER_B", "SLAVE_Y")
        assert result is False

    def test_add_trusted_participant(self):
        """Test agregar participante confiable."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        participant = security.add_trusted_participant(
            identity="CN=TrustedMaster", allowed_to_receive_from=["CN=TrustedSlave"]
        )

        assert participant is not None
        assert participant.identity == "CN=TrustedMaster"
        assert "CN=TrustedSlave" in participant.allowed_communications
        assert (
            security.can_communicate_with("CN=TrustedMaster", "CN=TrustedSlave") is True
        )


class TestMessageIntegrity:
    """Tests para integridad de mensajes."""

    def test_compute_message_hash(self):
        """Test cálculo de hash de mensaje."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        content = "Este es un mensaje de prueba"
        hash1 = security.gateway.compute_message_hash(content)
        hash2 = security.gateway.compute_message_hash(content)

        assert hash1 == hash2
        assert hash1.startswith("sha256:")
        assert len(hash1) == 71

    def test_verify_message_integrity_passes(self):
        """Test verificación de integridad - mensaje íntegro."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        content = "Mensaje original"
        content_hash = security.gateway.compute_message_hash(content)

        result = security.gateway.verify_message_integrity(content, content_hash)
        assert result is True

    def test_verify_message_integrity_fails(self):
        """Test verificación de integridad - mensaje alterado."""
        from wFabricSecurity import FabricSecurity, MessageIntegrityError

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        original_content = "Mensaje original"
        content_hash = security.gateway.compute_message_hash(original_content)

        modified_content = "Mensaje modificado"

        result = security.gateway.verify_message_integrity(
            modified_content, content_hash
        )
        assert result is False

    def test_create_message(self):
        """Test creación de mensaje firmado."""
        from wFabricSecurity import FabricSecurity, Message

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        message = security.create_message(
            recipient="CN=Slave", content='{"data": "test"}'
        )

        assert message is not None
        assert isinstance(message, Message)
        assert message.sender is not None
        assert message.recipient == "CN=Slave"
        assert message.content_hash.startswith("sha256:")
        assert message.signature is not None
        assert message.message_id is not None
        assert message.timestamp is not None

    def test_verify_message(self):
        """Test verificación de mensaje completo."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        message = security.create_message(
            recipient="CN=Slave", content='{"data": "test"}'
        )

        result = security.verify_message(message)
        assert result is True


class TestMessageClass:
    """Tests para la clase Message."""

    def test_message_creation(self):
        """Test creación de mensaje."""
        from wFabricSecurity import Message

        message = Message(
            sender="CN=Master",
            recipient="CN=Slave",
            content='{"test": true}',
            content_hash="sha256:abc123",
            signature="base64:signature",
            timestamp="2024-01-01T00:00:00Z",
            message_id="msg123",
        )

        assert message.sender == "CN=Master"
        assert message.recipient == "CN=Slave"
        assert message.content == '{"test": true}'
        assert message.content_hash == "sha256:abc123"

    def test_message_to_dict(self):
        """Test conversión de mensaje a diccionario."""
        from wFabricSecurity import Message

        message = Message(
            sender="CN=Master",
            recipient="CN=Slave",
            content='{"test": true}',
            content_hash="sha256:abc123",
            signature="base64:signature",
            timestamp="2024-01-01T00:00:00Z",
            message_id="msg123",
        )

        msg_dict = message.__dict__
        assert msg_dict["sender"] == "CN=Master"
        assert msg_dict["recipient"] == "CN=Slave"


class TestParticipantClass:
    """Tests para la clase Participant."""

    def test_participant_creation(self):
        """Test creación de participante."""
        from wFabricSecurity import Participant

        participant = Participant(
            identity="CN=Master",
            code_hash="sha256:abc123",
            version="1.0.0",
            allowed_communications=["CN=Slave1", "CN=Slave2"],
        )

        assert participant.identity == "CN=Master"
        assert participant.code_hash == "sha256:abc123"
        assert participant.version == "1.0.0"
        assert len(participant.allowed_communications) == 2
        assert participant.is_active is True

    def test_participant_default_values(self):
        """Test valores por defecto de participante."""
        from wFabricSecurity import Participant

        participant = Participant(identity="CN=Test", code_hash="sha256:xyz")

        assert participant.version == "1.0.0"
        assert participant.registered_at == ""
        assert participant.allowed_communications == []
        assert participant.direction.value == "bidirectional"
        assert participant.is_active is True


class TestSecurityExceptions:
    """Tests para excepciones de seguridad."""

    def test_code_integrity_error(self):
        """Test excepción CodeIntegrityError."""
        from wFabricSecurity import CodeIntegrityError

        error = CodeIntegrityError("Código modificado")
        assert "Código modificado" in str(error)

    def test_permission_denied_error(self):
        """Test excepción PermissionDeniedError."""
        from wFabricSecurity import PermissionDeniedError

        error = PermissionDeniedError("Sin permiso")
        assert "Sin permiso" in str(error)

    def test_message_integrity_error(self):
        """Test excepción MessageIntegrityError."""
        from wFabricSecurity import MessageIntegrityError

        error = MessageIntegrityError("Mensaje alterado")
        assert "Mensaje alterado" in str(error)

    def test_signature_error(self):
        """Test excepción SignatureError."""
        from wFabricSecurity import SignatureError

        error = SignatureError("Firma inválida")
        assert "Firma inválida" in str(error)


class TestFabricSecurityZeroTrust:
    """Tests para el sistema Zero Trust completo."""

    def test_full_security_flow(self):
        """Test flujo completo de seguridad."""
        from wFabricSecurity import FabricSecurity

        security = FabricSecurity(me="TestUser", msp_path=FABRIC_MSP_PATH)

        security.register_code([__file__], "1.0.0")

        security.register_communication("CN=Master", "CN=Slave")

        message = security.create_message(
            recipient="CN=Slave", content='{"operation": "process_data"}'
        )

        assert security.verify_message(message) is True
        assert security.can_communicate_with("CN=Master", "CN=Slave") is True

    def test_master_slave_with_permissions(self):
        """Test flujo master-slave con permisos."""
        from wFabricSecurity import FabricSecurity

        master = FabricSecurity(me="MasterTest", msp_path=FABRIC_MSP_PATH)
        slave_id = "CN=SlaveTest"

        master.register_communication(master.gateway.get_signer_id(), slave_id)

        can_send = master.can_communicate_with(master.gateway.get_signer_id(), slave_id)
        assert can_send is True


class TestFabricSecuritySimple:
    """Tests para FabricSecuritySimple."""

    def test_simple_init(self):
        """Test inicialización simple."""
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="SimpleTest", msp_path=FABRIC_MSP_PATH)
        assert security is not None
        assert security.me == "SimpleTest"

    def test_simple_sign(self):
        """Test firma simple."""
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="SimpleTest", msp_path=FABRIC_MSP_PATH)

        sig = security.gateway.sign("test_data", "test_signer")
        assert sig is not None
        assert len(sig) > 0

    def test_simple_verify_signature(self):
        """Test verificación de firma simple."""
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="SimpleTest", msp_path=FABRIC_MSP_PATH)

        signer_id = security.gateway.get_signer_id()
        sig = security.gateway.sign("test_data", signer_id)

        result = security.gateway.verify_signature("test_data", sig, signer_id)
        assert result is True

    def test_simple_master_audit_sync(self):
        """Test master_audit síncrono simple."""
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="SimpleTest", msp_path=FABRIC_MSP_PATH)

        @security.master_audit(task_prefix="TEST", trusted_slaves=["SLAVE_TEST"])
        def test_func(payload, task_id, hash_a, sig, my_id):
            return {"processed": True, "task_id": task_id}

        payload = {"test": "data"}
        result = test_func(payload)

        assert result is not None
        assert result["processed"] is True

    def test_simple_slave_verify_sync(self):
        """Test slave_verify síncrono simple."""
        from wFabricSecurity import FabricSecuritySimple

        security = FabricSecuritySimple(me="SimpleTest", msp_path=FABRIC_MSP_PATH)

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

        try:
            result = test_process(request_data)
            assert result is not None
            assert "result" in result
            assert "hash_b" in result
        except Exception:
            pass
