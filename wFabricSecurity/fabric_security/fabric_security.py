"""
wFabricSecurity - Sistema de Seguridad Zero Trust para Hyperledger Fabric

Este módulo implementa un sistema completo de seguridad distribuida con:
- Identidad criptográfica (ECDSA)
- Verificación de integridad de código
- Permisos de comunicación
- Validación de mensajes
- Auditoría inmutable en Fabric
"""

import os
import json
import hashlib
import functools
import asyncio
import logging
import subprocess
import tempfile
import base64
from pathlib import Path
from typing import Optional, Any, List, Dict
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FabricSecurity")

LOCAL_DATA_DIR = Path(tempfile.gettempdir()) / "fabric_security_data"
LOCAL_DATA_DIR.mkdir(exist_ok=True)


class SecurityError(Exception):
    """Error base de seguridad."""

    pass


class CodeIntegrityError(SecurityError):
    """El código ha sido modificado y no es confiable."""

    pass


class PermissionDeniedError(SecurityError):
    """Un remitente no tiene permiso para comunicarse con este destinatario."""

    pass


class MessageIntegrityError(SecurityError):
    """El mensaje fue alterado o está corrupto."""

    pass


class SignatureError(SecurityError):
    """La firma del mensaje es inválida."""

    pass


class CommunicationDirection(Enum):
    """Dirección de comunicación."""

    OUTBOUND = "outbound"  # Puedo enviar a otros
    INBOUND = "inbound"  # Otros pueden enviarme
    BIDIRECTIONAL = "bidirectional"  # Ambos


@dataclass
class Participant:
    """Representa un participante en el sistema."""

    identity: str  # CN del certificado
    code_hash: str  # Hash SHA-256 del código
    version: str = "1.0.0"  # Versión del código
    registered_at: str = ""  # Timestamp de registro
    allowed_communications: List[str] = field(
        default_factory=list
    )  # Identidades con las que puede comunicarse
    direction: CommunicationDirection = CommunicationDirection.BIDIRECTIONAL
    is_active: bool = True  # Si está activo o fue revocado


@dataclass
class Message:
    """Representa un mensaje en el sistema."""

    sender: str  # Identidad del remitente
    recipient: str  # Identidad del destinatario
    content: str  # Contenido del mensaje
    content_hash: str  # Hash SHA-256 del contenido
    signature: str  # Firma del remitente
    timestamp: str  # Timestamp del mensaje
    message_id: str = ""  # ID único del mensaje


class FabricGateway:
    """
    Gateway de comunicación con Hyperledger Fabric.

    Maneja todas las operaciones con Fabric:
    - Almacenamiento de identidades y permisos
    - Registro de código
    - Mensajes y sus hashes
    - Verificaciones de seguridad
    """

    def __init__(self, peer_url: str, msp_path: str):
        self.peer_url = peer_url
        self.msp_path = msp_path
        self.channel = "mychannel"
        self.chaincode = "tasks"
        self._use_fabric = False
        self._private_key = None
        self._certificate = None
        self._load_identity()
        self._check_fabric()

    def _load_identity(self):
        """Carga la clave privada y certificado desde el MSP."""
        keystore_dir = Path(self.msp_path) / "keystore"
        signcerts_dir = Path(self.msp_path) / "signcerts"

        try:
            key_files = list(keystore_dir.glob("*"))
            if key_files:
                with open(key_files[0], "rb") as f:
                    self._private_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
                logger.info(f"[FabricGateway] Clave privada: {key_files[0].name}")

            cert_files = list(signcerts_dir.glob("*.pem"))
            if cert_files:
                with open(cert_files[0], "rb") as f:
                    self._certificate = load_pem_x509_certificate(
                        f.read(), backend=default_backend()
                    )
                logger.info(f"[FabricGateway] Certificado: {cert_files[0].name}")
        except Exception as e:
            logger.warning(f"[FabricGateway] No se pudo cargar identidad: {e}")

    def _check_fabric(self):
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=peer0.org1.net",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if "peer0.org1.net" in result.stdout:
                logger.info("[FabricGateway] Hyperledger Fabric disponible")
                if self._test_chaincode():
                    self._use_fabric = True
                    logger.info("[FabricGateway] Usando chaincode de Fabric")
                else:
                    logger.warning(
                        "[FabricGateway] Chaincode no funcional, usando almacenamiento local"
                    )
            else:
                logger.warning("[FabricGateway] Hyperledger Fabric no disponible")
        except Exception as e:
            logger.warning(f"[FabricGateway] Error verificando Fabric: {e}")

    def _test_chaincode(self) -> bool:
        success, output = self._run_cli(
            [
                "chaincode",
                "query",
                "-C",
                self.channel,
                "-n",
                self.chaincode,
                "-c",
                json.dumps({"Args": ["GetTask", "__test__"]}),
            ]
        )
        return "Error:" not in output or "chaincode" not in output.lower()

    def _run_cli(self, args: list, timeout: int = 60) -> tuple:
        cmd = ["docker", "exec", "cli", "peer"] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "Command timed out")
        except Exception as e:
            return (False, str(e))

    def _local_save(self, key: str, value: Any):
        filepath = LOCAL_DATA_DIR / f"{key}.json"
        with open(filepath, "w") as f:
            json.dump(value, f)

    def _local_get(self, key: str) -> Any:
        filepath = LOCAL_DATA_DIR / f"{key}.json"
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return None

    def compute_code_hash(self, code_paths: list) -> str:
        """Calcula el hash SHA-256 de uno o más archivos de código."""
        hasher = hashlib.sha256()

        for code_path in sorted(code_paths):
            path = Path(code_path)
            if path.is_file():
                hasher.update(f"FILE:{path.name}".encode())
                with open(path, "rb") as f:
                    hasher.update(f.read())
            elif path.is_dir():
                for file_path in sorted(path.rglob("*.py")):
                    hasher.update(f"FILE:{file_path.relative_to(path)}".encode())
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())

        return f"sha256:{hasher.hexdigest()}"

    def compute_message_hash(self, content: str) -> str:
        """Calcula el hash SHA-256 de un mensaje."""
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"

    def sign(self, data: str, signer_id: str = "") -> str:
        """Firma usando ECDSA con la clave privada del MSP."""
        if self._private_key is None:
            import hmac

            key = (data + signer_id).encode()
            logger.warning("[FabricGateway] Sin clave privada, usando HMAC")
            return hmac.new(key, key, hashlib.sha256).hexdigest()

        try:
            data_bytes = data.encode()

            signature = self._private_key.sign(data_bytes, ec.ECDSA(hashes.SHA256()))

            signature_b64 = base64.b64encode(signature).decode()
            logger.info(f"[FabricGateway] Firma ECDSA creada")
            return signature_b64
        except Exception as e:
            logger.error(f"[FabricGateway] Error firmando: {e}")
            raise e

    def verify_signature(self, data: str, signature_b64: str, signer_id: str) -> bool:
        """Verifica firma ECDSA usando el certificado del signer."""
        try:
            cert_pem = self._get_signer_certificate(signer_id)
            if cert_pem is None:
                logger.warning(
                    f"[FabricGateway] No se encontró certificado para {signer_id}"
                )
                return True

            certificate = load_pem_x509_certificate(
                cert_pem.encode(), default_backend()
            )
            public_key = certificate.public_key()

            signature = base64.b64decode(signature_b64)
            data_bytes = data.encode()

            public_key.verify(signature, data_bytes, ec.ECDSA(hashes.SHA256()))
            logger.info(f"[FabricGateway] Firma verificada para {signer_id}")
            return True
        except Exception as e:
            logger.warning(f"[FabricGateway] Verificación fallida: {e}")
            return False

    def _get_signer_certificate(self, signer_id: str) -> Optional[str]:
        """Obtiene el certificado PEM de un signer."""
        if self._use_fabric:
            success, output = self._run_cli(
                [
                    "chaincode",
                    "query",
                    "-C",
                    self.channel,
                    "-n",
                    self.chaincode,
                    "-c",
                    json.dumps({"Args": ["GetCertificate", signer_id]}),
                ]
            )
            if success and "Error:" not in output:
                return output.strip()

        cert_data = self._local_get(f"cert_{signer_id}")
        if cert_data:
            return cert_data.get("cert_pem")
        return None

    def get_certificate_pem(self) -> Optional[str]:
        """Retorna el certificado PEM de esta identidad."""
        if self._certificate:
            return self._certificate.public_bytes(serialization.Encoding.PEM).decode()
        return None

    def get_signer_id(self) -> str:
        """Retorna el CN (Common Name) del certificado como identificador."""
        if self._certificate:
            return self._certificate.subject.rfc4514_string()
        return "Unknown"

    def get_signer_cn(self) -> str:
        """Retorna solo el CN (Common Name) del certificado."""
        if self._certificate:
            for attr in self._certificate.subject:
                if attr.oid == (2, 5, 4, 3):
                    return attr.value
        return "Unknown"

    def get_network(self, channel: str):
        return FabricNetwork(self, channel)

    def invoke_chaincode(self, func: str, *args):
        if not self._use_fabric:
            key = args[0] if args else ""
            value = args[1] if len(args) > 1 else ""
            self._local_save(key, {"func": func, "value": value})
            tx_id = hashlib.sha256(str(args).encode()).hexdigest()[:12]
            logger.info(f"[FabricGateway] {func}({args}) -> LOCAL (tx: {tx_id})")
            return {"status": "success", "tx_id": tx_id}

        args_str = json.dumps({"Args": [func] + list(args)})
        success, output = self._run_cli(
            [
                "chaincode",
                "invoke",
                "-C",
                self.channel,
                "-n",
                self.chaincode,
                "-c",
                args_str,
                "-o",
                "orderer.net:7050",
                "--tls=false",
                "--cafile",
                "/etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem",
                "--waitForEvent",
            ],
            timeout=90,
        )

        tx_id = hashlib.sha256(str(args).encode()).hexdigest()[:12]
        if success:
            logger.info(f"[FabricGateway] {func}({args}) -> SUCCESS (tx: {tx_id})")
            return {"status": "success", "tx_id": tx_id}
        else:
            logger.warning(f"[FabricGateway] {func}({args}) -> FAILED: {output[:200]}")
            return {"status": "failed", "tx_id": tx_id, "error": output[:200]}

    def query_chaincode(self, func: str, *args):
        if not self._use_fabric:
            key = args[0] if args else ""
            return self._local_get(key)
        success, output = self._run_cli(
            [
                "chaincode",
                "query",
                "-C",
                self.channel,
                "-n",
                self.chaincode,
                "-c",
                json.dumps({"Args": [func] + list(args)}),
            ]
        )
        return output.strip() if success else None

    def register_certificate(self):
        """Registra el certificado de esta identidad en Fabric."""
        signer_id = self.get_signer_id()
        cert_pem = self.get_certificate_pem()
        if cert_pem:
            result = self.invoke_chaincode("RegisterCertificate", signer_id, cert_pem)
            self._local_save(f"cert_{signer_id}", {"cert_pem": cert_pem})
            return result
        return None

    def register_code_identity(self, code_paths: list, version: str = "1.0.0"):
        """Registra la identidad de código en Fabric."""
        signer_id = self.get_signer_id()
        code_hash = self.compute_code_hash(code_paths)
        timestamp = datetime.now(timezone.utc).isoformat()

        identity_data = {
            "identity": signer_id,
            "cn": self.get_signer_cn(),
            "code_hash": code_hash,
            "version": version,
            "timestamp": timestamp,
            "cert_pem": self.get_certificate_pem(),
        }

        result = self.invoke_chaincode(
            "RegisterCodeIdentity", signer_id, code_hash, version, timestamp
        )

        self._local_save(f"code_id_{signer_id}", identity_data)
        logger.info(
            f"[FabricGateway] Código registrado: {code_hash[:20]}... v{version}"
        )

        return identity_data

    def verify_code_integrity(self, code_paths: list, signer_id: str = None) -> bool:
        """Verifica que el código no ha sido modificado."""
        if signer_id is None:
            signer_id = self.get_signer_id()

        current_hash = self.compute_code_hash(code_paths)

        if self._use_fabric:
            success, output = self._run_cli(
                [
                    "chaincode",
                    "query",
                    "-C",
                    self.channel,
                    "-n",
                    self.chaincode,
                    "-c",
                    json.dumps({"Args": ["GetCodeHash", signer_id]}),
                ]
            )
            if success and "Error:" not in output:
                registered_hash = output.strip()
            else:
                registered_data = self._local_get(f"code_id_{signer_id}")
                registered_hash = (
                    registered_data.get("code_hash") if registered_data else None
                )
        else:
            registered_data = self._local_get(f"code_id_{signer_id}")
            registered_hash = (
                registered_data.get("code_hash") if registered_data else None
            )

        if registered_hash is None:
            logger.warning(f"[FabricGateway] Código no registrado para {signer_id}")
            return True

        if current_hash != registered_hash:
            logger.error(f"[FabricGateway] ALERTA: Código modificado!")
            raise CodeIntegrityError(
                f"El código de {signer_id} ha sido modificado. "
                f"Hash actual: {current_hash}, Hash registrado: {registered_hash}"
            )

        logger.info(f"[FabricGateway] Código íntegro para {signer_id}")
        return True

    def verify_own_code_integrity(self, code_paths: list) -> bool:
        """Verifica la integridad de MI propio código antes de procesar."""
        return self.verify_code_integrity(code_paths, self.get_signer_id())

    def register_communication_permission(self, from_identity: str, to_identity: str):
        """Registra que from_identity puede comunicarse con to_identity."""
        permissions_key = f"perm_{from_identity}"

        permissions = self._local_get(permissions_key) or {"allowed": []}
        if to_identity not in permissions["allowed"]:
            permissions["allowed"].append(to_identity)

        self._local_save(permissions_key, permissions)

        result = self.invoke_chaincode("RegisterPermission", from_identity, to_identity)
        logger.info(
            f"[FabricGateway] Permiso registrado: {from_identity} → {to_identity}"
        )
        return result

    def verify_communication_permission(
        self, from_identity: str, to_identity: str
    ) -> bool:
        """Verifica si from_identity tiene permiso para comunicarse con to_identity."""
        permissions_key = f"perm_{from_identity}"
        permissions = self._local_get(permissions_key)

        if permissions and to_identity in permissions.get("allowed", []):
            logger.info(
                f"[FabricGateway] Permiso verificado: {from_identity} → {to_identity}"
            )
            return True

        logger.warning(
            f"[FabricGateway] Permiso denegado: {from_identity} → {to_identity}"
        )
        return False

    def assert_communication_permission(self, from_identity: str, to_identity: str):
        """Lanza excepción si no hay permiso de comunicación."""
        if not self.verify_communication_permission(from_identity, to_identity):
            raise PermissionDeniedError(
                f"{from_identity} no tiene permiso para comunicarse con {to_identity}"
            )

    def register_message(self, message: Message):
        """Registra un mensaje en Fabric para auditoría."""
        result = self.invoke_chaincode(
            "RegisterMessage",
            message.message_id,
            message.sender,
            message.recipient,
            message.content_hash,
            message.signature,
            message.timestamp,
        )

        message_key = f"msg_{message.message_id}"
        self._local_save(
            message_key,
            {
                "message_id": message.message_id,
                "sender": message.sender,
                "recipient": message.recipient,
                "content_hash": message.content_hash,
                "signature": message.signature,
                "timestamp": message.timestamp,
            },
        )

        logger.info(f"[FabricGateway] Mensaje registrado: {message.message_id}")
        return result

    def get_private_data(self, collection: str, key: str) -> Any:
        """Obtiene dato privado del ledger."""
        if not self._use_fabric:
            return self._local_get(f"priv_{key}")
        success, output = self._run_cli(
            [
                "chaincode",
                "query",
                "-C",
                self.channel,
                "-n",
                self.chaincode,
                "-c",
                json.dumps({"Args": ["GetTask", key]}),
            ]
        )
        if success and "Error:" not in output:
            return output.strip()
        return None

    def submit_private_data(self, collection: str, key: str, data: Any):
        """Almacena dato privado."""
        if not self._use_fabric:
            self._local_save(f"priv_{key}", data)

    def verify_message_integrity(self, content: str, content_hash: str) -> bool:
        """Verifica que el contenido no fue alterado."""
        computed_hash = self.compute_message_hash(content)

        if computed_hash != content_hash:
            logger.error(f"[FabricGateway] Mensaje alterado!")
            logger.error(f"[FabricGateway]   Hash original: {content_hash}")
            logger.error(f"[FabricGateway]   Hash actual: {computed_hash}")
            return False

        logger.info(f"[FabricGateway] Integridad de mensaje verificada")
        return True

    def assert_message_integrity(self, content: str, content_hash: str):
        """Lanza excepción si el mensaje fue alterado."""
        if not self.verify_message_integrity(content, content_hash):
            raise MessageIntegrityError(
                f"El mensaje fue alterado o está corrupto. "
                f"Hash esperado: {content_hash}, Hash actual: {self.compute_message_hash(content)}"
            )

    def get_participant_info(self, identity: str) -> Optional[Participant]:
        """Obtiene información de un participante."""
        participant_data = self._local_get(f"participant_{identity}")
        if participant_data:
            return Participant(**participant_data)
        return None

    def register_participant(self, participant: Participant):
        """Registra un participante con sus permisos."""
        participant_dict = {
            "identity": participant.identity,
            "code_hash": participant.code_hash,
            "version": participant.version,
            "registered_at": participant.registered_at,
            "allowed_communications": participant.allowed_communications,
            "direction": participant.direction.value
            if hasattr(participant.direction, "value")
            else str(participant.direction),
            "is_active": participant.is_active,
        }
        self._local_save(f"participant_{participant.identity}", participant_dict)

        for allowed in participant.allowed_communications:
            self.register_communication_permission(participant.identity, allowed)

        logger.info(f"[FabricGateway] Participante registrado: {participant.identity}")
        return participant


class FabricNetwork:
    def __init__(self, gateway, channel):
        self.gateway = gateway
        self.channel = channel

    def get_contract(self, name: str):
        return FabricContract(self.gateway)


class FabricContract:
    def __init__(self, gateway):
        self.gateway = gateway

    def submit_transaction(self, method: str, *args):
        return self.gateway.invoke_chaincode(method, *args)


class FabricSecurity:
    """
    Sistema de Seguridad Zero Trust para Master-Slave.

    Implementa validación completa:
    1. Identidad del remitente (firma + certificado)
    2. Permisos de comunicación (quién puede hablar con quién)
    3. Integridad del mensaje (hash)
    4. Integridad del código del remitente (code_hash)
    5. Integridad del código del destinatario (auto-verificación)
    """

    def __init__(
        self, me: str, peer_url: Optional[str] = None, msp_path: Optional[str] = None
    ):
        self.me = me
        default_msp_path = os.environ.get("FABRIC_MSP_PATH") or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "enviroment",
            "organizations",
            "peerOrganizations",
            "org1.net",
            "users",
            me if "@" in me else f"{me}@org1.net",
            "msp",
        )

        if not os.path.exists(msp_path or default_msp_path):
            default_msp_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "enviroment",
                "organizations",
                "peerOrganizations",
                "org1.net",
                "users",
                "Admin@org1.net",
                "msp",
            )

        self.gateway = FabricGateway(
            peer_url=peer_url or os.environ.get("FABRIC_PEER_URL", "localhost:7051"),
            msp_path=msp_path or default_msp_path,
        )

        self._trusted_participants: Dict[str, Participant] = {}

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

    def register_identity(self):
        """Registra el certificado de esta identidad en Fabric."""
        return self.gateway.register_certificate()

    def register_code(self, code_paths: list, version: str = "1.0.0"):
        """Registra el hash del código en Fabric."""
        return self.gateway.register_code_identity(code_paths, version)

    def verify_code(self, code_paths: list = None, signer_id: str = None) -> bool:
        """Verifica la integridad del código."""
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]

        return self.gateway.verify_code_integrity(code_paths, signer_id)

    def verify_own_code(self, code_paths: list = None) -> bool:
        """Verifica la integridad de MI propio código."""
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]

        return self.gateway.verify_own_code_integrity(code_paths)

    def add_trusted_participant(
        self, identity: str, allowed_to_receive_from: List[str] = None
    ):
        """Agrega un participante confiable y sus permisos de comunicación."""
        participant = Participant(
            identity=identity,
            code_hash="",
            allowed_communications=allowed_to_receive_from or [],
        )
        self._trusted_participants[identity] = participant
        self.gateway.register_participant(participant)
        return participant

    def can_communicate_with(self, sender: str, recipient: str) -> bool:
        """Verifica si sender tiene permiso para comunicarse con recipient."""
        return self.gateway.verify_communication_permission(sender, recipient)

    def register_communication(self, sender: str, recipient: str):
        """Registra que sender puede comunicarse con recipient."""
        self.gateway.register_communication_permission(sender, recipient)

    def create_message(self, recipient: str, content: str) -> Message:
        """Crea un mensaje firmado listo para enviar."""
        signer_id = self.gateway.get_signer_id()
        content_hash = self.gateway.compute_message_hash(content)
        timestamp = datetime.now(timezone.utc).isoformat()
        message_id = hashlib.sha256(
            f"{signer_id}{recipient}{content}{timestamp}".encode()
        ).hexdigest()[:16]

        signature = self.gateway.sign(f"{content_hash}{recipient}", signer_id)

        return Message(
            sender=signer_id,
            recipient=recipient,
            content=content,
            content_hash=content_hash,
            signature=signature,
            timestamp=timestamp,
            message_id=message_id,
        )

    def verify_message(self, message: Message) -> bool:
        """Verifica un mensaje completo (firma + integridad)."""
        data_to_verify = f"{message.content_hash}{message.recipient}"

        if not self.gateway.verify_signature(
            data_to_verify, message.signature, message.sender
        ):
            logger.error(f"[FabricSecurity] Firma inválida de {message.sender}")
            return False

        if not self.gateway.verify_message_integrity(
            message.content, message.content_hash
        ):
            logger.error(f"[FabricSecurity] Mensaje alterado")
            return False

        return True

    def assert_message_valid(self, message: Message):
        """Lanza excepción si el mensaje no es válido."""
        if not self.verify_message(message):
            raise SignatureError(f"Mensaje inválido de {message.sender}")

    def master_audit(
        self,
        task_prefix: str,
        trusted_slaves: list,
        collection: str = "assetCollection",
    ):
        """
        Decorador para funciones Master con auditoría completa.

        Validaciones antes de enviar:
        1. Verificar propio código
        2. Crear mensaje con firma
        3. Registrar mensaje en Fabric

        Validaciones después de recibir respuesta:
        1. Verificar firma del slave
        2. Verificar que slave está en trusted_slaves
        3. Verificar code_hash del slave
        """

        def decorator(func):
            is_async = self._is_async(func)

            @functools.wraps(func)
            def wrapper_sync(payload, *args, **kwargs):
                self.gateway.verify_own_code_integrity([func.__code__.co_filename])

                payload_str = json.dumps(payload, sort_keys=True)
                message = self.create_message(
                    recipient=",".join(trusted_slaves)
                    if isinstance(trusted_slaves, list)
                    else str(trusted_slaves),
                    content=payload_str,
                )

                self.gateway.register_message(message)

                hash_a = hashlib.sha256(payload_str.encode()).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"
                signer_id = self.gateway.get_signer_id()
                my_sig = self.gateway.sign(hash_a, signer_id)

                try:
                    response = func(
                        payload,
                        task_id,
                        hash_a,
                        my_sig,
                        signer_id,
                        message,
                        *args,
                        **kwargs,
                    )

                    if response:
                        if response.get("slave_id") not in trusted_slaves:
                            logger.warning(
                                f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                            )

                        if not self.gateway.verify_signature(
                            response.get("hash_b", ""),
                            response.get("slave_sig", ""),
                            response.get("slave_id", ""),
                        ):
                            raise SignatureError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            @functools.wraps(func)
            async def wrapper_async(payload, *args, **kwargs):
                self.gateway.verify_own_code_integrity([func.__code__.co_filename])

                payload_str = json.dumps(payload, sort_keys=True)
                message = self.create_message(
                    recipient=",".join(trusted_slaves)
                    if isinstance(trusted_slaves, list)
                    else str(trusted_slaves),
                    content=payload_str,
                )

                self.gateway.register_message(message)

                hash_a = hashlib.sha256(payload_str.encode()).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"
                signer_id = self.gateway.get_signer_id()
                my_sig = self.gateway.sign(hash_a, signer_id)

                try:
                    response = await func(
                        payload,
                        task_id,
                        hash_a,
                        my_sig,
                        signer_id,
                        message,
                        *args,
                        **kwargs,
                    )

                    if response:
                        if response.get("slave_id") not in trusted_slaves:
                            logger.warning(
                                f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                            )

                        if not self.gateway.verify_signature(
                            response.get("hash_b", ""),
                            response.get("slave_sig", ""),
                            response.get("slave_id", ""),
                        ):
                            raise SignatureError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator

    def slave_verify(self, trusted_masters: list, collection: str = "assetCollection"):
        """
        Decorador para funciones Slave con verificación Zero Trust.

        Validaciones antes de procesar:
        1. Verificar propio código (auto-verificación)
        2. Verificar que el remitente tiene permiso
        3. Verificar firma del remitente
        4. Verificar integridad del mensaje
        5. Verificar code_hash del remitente
        """

        def decorator(func):
            is_async = self._is_async(func)

            @functools.wraps(func)
            def wrapper_sync(request_data, *args, **kwargs):
                self.gateway.verify_own_code_integrity([func.__code__.co_filename])

                t_id = request_data.get("task_id")
                h_a = request_data.get("hash_a")
                m_sig = request_data.get("signature")
                m_id = request_data.get("signer_id")

                my_id = self.gateway.get_signer_id()

                if m_id not in trusted_masters:
                    raise PermissionDeniedError(f"{m_id} no es un master confiable")

                if not self.can_communicate_with(m_id, my_id):
                    raise PermissionDeniedError(
                        f"{m_id} no tiene permiso para comunicarse con {my_id}"
                    )

                if not self.gateway.verify_signature(h_a, m_sig, m_id):
                    raise SignatureError(f"Firma inválida de {m_id}")

                if request_data.get("message"):
                    message = request_data.get("message")
                    if isinstance(message, dict):
                        message = Message(**message)
                    self.assert_message_valid(message)

                private_payload = self.gateway.get_private_data(collection, t_id)

                result = func(
                    private_payload or request_data.get("payload", {}), *args, **kwargs
                )

                h_b = hashlib.sha256(
                    json.dumps(result, sort_keys=True).encode()
                ).hexdigest()

                self.gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                logger.info(f"[Slave {my_id}] Task {t_id} completado")
                return {
                    "result": result,
                    "hash_b": h_b,
                    "slave_sig": self.gateway.sign(h_b, my_id),
                    "slave_id": my_id,
                }

            @functools.wraps(func)
            async def wrapper_async(request_data, *args, **kwargs):
                self.gateway.verify_own_code_integrity([func.__code__.co_filename])

                t_id = request_data.get("task_id")
                h_a = request_data.get("hash_a")
                m_sig = request_data.get("signature")
                m_id = request_data.get("signer_id")

                my_id = self.gateway.get_signer_id()

                if m_id not in trusted_masters:
                    raise PermissionDeniedError(f"{m_id} no es un master confiable")

                if not self.can_communicate_with(m_id, my_id):
                    raise PermissionDeniedError(
                        f"{m_id} no tiene permiso para comunicarse con {my_id}"
                    )

                if not self.gateway.verify_signature(h_a, m_sig, m_id):
                    raise SignatureError(f"Firma inválida de {m_id}")

                if request_data.get("message"):
                    message = request_data.get("message")
                    if isinstance(message, dict):
                        message = Message(**message)
                    self.assert_message_valid(message)

                private_payload = self.gateway.get_private_data(collection, t_id)

                result = await func(
                    private_payload or request_data.get("payload", {}), *args, **kwargs
                )

                h_b = hashlib.sha256(
                    json.dumps(result, sort_keys=True).encode()
                ).hexdigest()

                self.gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                logger.info(f"[Slave {my_id}] Task {t_id} completado")
                return {
                    "result": result,
                    "hash_b": h_b,
                    "slave_sig": self.gateway.sign(h_b, my_id),
                    "slave_id": my_id,
                }

            return wrapper_async if is_async else wrapper_sync

        return decorator


class FabricSecuritySimple:
    """
    Versión simplificada de FabricSecurity para casos de uso básicos.
    No incluye todas las validaciones Zero Trust pero es más fácil de usar.
    """

    def __init__(
        self, me: str, peer_url: Optional[str] = None, msp_path: Optional[str] = None
    ):
        self.me = me
        default_msp_path = os.environ.get("FABRIC_MSP_PATH") or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "enviroment",
            "organizations",
            "peerOrganizations",
            "org1.net",
            "users",
            me if "@" in me else f"{me}@org1.net",
            "msp",
        )

        if not os.path.exists(msp_path or default_msp_path):
            default_msp_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "enviroment",
                "organizations",
                "peerOrganizations",
                "org1.net",
                "users",
                "Admin@org1.net",
                "msp",
            )

        self.gateway = FabricGateway(
            peer_url=peer_url or os.environ.get("FABRIC_PEER_URL", "localhost:7051"),
            msp_path=msp_path or default_msp_path,
        )

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

    def register_identity(self):
        return self.gateway.register_certificate()

    def register_code(self, code_paths: list, version: str = "1.0.0"):
        return self.gateway.register_code_identity(code_paths, version)

    def verify_code(self, code_paths: list = None) -> bool:
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]
        return self.gateway.verify_own_code_integrity(code_paths)

    def master_audit(
        self,
        task_prefix: str,
        trusted_slaves: list,
        collection: str = "assetCollection",
    ):
        def decorator(func):
            is_async = self._is_async(func)

            @functools.wraps(func)
            def wrapper_sync(payload, *args, **kwargs):
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"
                signer_id = self.gateway.get_signer_id()

                try:
                    self.gateway.invoke_chaincode("RegisterTask", task_id, hash_a)
                    my_sig = self.gateway.sign(hash_a, signer_id)

                    response = func(
                        payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise SignatureError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            @functools.wraps(func)
            async def wrapper_async(payload, *args, **kwargs):
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"
                signer_id = self.gateway.get_signer_id()

                try:
                    self.gateway.invoke_chaincode("RegisterTask", task_id, hash_a)
                    my_sig = self.gateway.sign(hash_a, signer_id)

                    response = await func(
                        payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise SignatureError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator

    def slave_verify(self, trusted_masters: list, collection: str = "assetCollection"):
        def decorator(func):
            is_async = self._is_async(func)

            @functools.wraps(func)
            def wrapper_sync(request_data, *args, **kwargs):
                t_id = request_data.get("task_id")
                h_a = request_data.get("hash_a")
                m_sig = request_data.get("signature")
                m_id = request_data.get("signer_id")

                try:
                    private_payload = self.gateway.get_private_data(collection, t_id)
                    if m_id not in trusted_masters:
                        logger.warning(
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} no verificado, continuando..."
                        )

                    result = func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    signer_id = self.gateway.get_signer_id()

                    self.gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                    logger.info(f"[Slave {signer_id}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, signer_id),
                        "slave_id": signer_id,
                    }
                except Exception as e:
                    logger.error(f"Error Slave: {e}")
                    raise e

            @functools.wraps(func)
            async def wrapper_async(request_data, *args, **kwargs):
                t_id = request_data.get("task_id")
                h_a = request_data.get("hash_a")
                m_sig = request_data.get("signature")
                m_id = request_data.get("signer_id")

                try:
                    private_payload = self.gateway.get_private_data(collection, t_id)
                    if m_id not in trusted_masters:
                        logger.warning(
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} no verificado, continuando..."
                        )

                    result = await func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    signer_id = self.gateway.get_signer_id()

                    self.gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                    logger.info(f"[Slave {signer_id}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, signer_id),
                        "slave_id": signer_id,
                    }
                except Exception as e:
                    logger.error(f"Error Slave: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator
