"""
wFabricSecurity - Zero Trust Security System for Hyperledger Fabric

This module implements a complete distributed security system with:
- Cryptographic identity (ECDSA)
- Code integrity verification
- Communication permissions
- Message validation
- Immutable audit on Fabric
"""

import asyncio
import functools
import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

from .core import (
    CodeIntegrityError,
    CommunicationDirection,
    Message,
    MessageIntegrityError,
    Participant,
    PermissionDeniedError,
    RateLimitError,
    RevocationError,
    SecurityError,
    SignatureError,
)
from .crypto import HashingService, IdentityManager, SigningService
from .fabric import FabricContract
from .fabric import FabricGateway as BaseFabricGateway
from .fabric import FabricNetwork
from .security import IntegrityVerifier, MessageManager, PermissionManager, RateLimiter
from .security import master_audit as base_master_audit
from .security import slave_verify as base_slave_verify
from .security import with_retry

logger = logging.getLogger("FabricSecurity")


class FabricGateway(BaseFabricGateway):
    """Extended Fabric Gateway with all features."""

    pass


class FabricSecurity:
    """
    Zero Trust Security System for Master-Slave.

    Implements complete validation:
    1. Sender identity (signature + certificate)
    2. Communication permissions (who can talk to whom)
    3. Message integrity (hash)
    4. Sender code integrity (code_hash)
    5. Recipient code integrity (self-verification)
    """

    def __init__(
        self,
        me: str,
        peer_url: Optional[str] = None,
        msp_path: Optional[str] = None,
        rate_limit_rps: float = 100,
        rate_limit_burst: int = 200,
        message_ttl: int = 3600,
    ):
        """Initialize FabricSecurity.

        Args:
            me: Identity name
            peer_url: Fabric peer URL
            msp_path: Path to MSP directory
            rate_limit_rps: Rate limit requests per second
            rate_limit_burst: Rate limit burst size
            message_ttl: Message TTL in seconds
        """
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
        self._rate_limiter = RateLimiter(rate_limit_rps, rate_limit_burst)
        self._message_manager = MessageManager(self.gateway, ttl_seconds=message_ttl)
        self._integrity_verifier = IntegrityVerifier(self.gateway)
        self._permission_manager = PermissionManager(self.gateway)

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get rate limiter."""
        return self._rate_limiter

    @property
    def message_manager(self) -> MessageManager:
        """Get message manager."""
        return self._message_manager

    @property
    def integrity_verifier(self) -> IntegrityVerifier:
        """Get integrity verifier."""
        return self._integrity_verifier

    @property
    def permission_manager(self) -> PermissionManager:
        """Get permission manager."""
        return self._permission_manager

    def get_signer_id(self) -> str:
        """Get current signer identity."""
        return self.gateway.get_signer_id()

    def get_signer_cn(self) -> str:
        """Get current signer Common Name."""
        return self.gateway.get_signer_cn()

    def is_using_fabric(self) -> bool:
        """Check if using Fabric backend."""
        return self.gateway.is_using_fabric

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

    def register_identity(self) -> dict:
        """Register the certificate of this identity in Fabric."""
        return self.gateway.register_certificate()

    def register_code(self, code_paths: list, version: str = "1.0.0") -> dict:
        """Register the code hash in Fabric."""
        return self.gateway.register_code_identity(code_paths, version)

    def verify_code(self, code_paths: list = None, signer_id: str = None) -> bool:
        """Verify code integrity."""
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]
        return self.gateway.verify_code_integrity(code_paths, signer_id)

    def verify_own_code(self, code_paths: list = None) -> bool:
        """Verify integrity of own code."""
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]
        return self.gateway.verify_own_code_integrity(code_paths)

    def compute_code_hash(self, code_paths: list) -> str:
        """Compute hash of code files."""
        return self.gateway.compute_code_hash(code_paths)

    def compute_message_hash(self, content: str) -> str:
        """Compute hash of message content."""
        return self.gateway.compute_message_hash(content)

    def sign(self, data: str, signer_id: str = "") -> str:
        """Sign data."""
        return self.gateway.sign(data, signer_id)

    def verify_signature(self, data: str, signature: str, signer_id: str) -> bool:
        """Verify signature."""
        return self.gateway.verify_signature(data, signature, signer_id)

    def add_trusted_participant(
        self, identity: str, allowed_to_receive_from: List[str] = None
    ) -> Participant:
        """Add a trusted participant and their communication permissions."""
        participant = Participant(
            identity=identity,
            code_hash="",
            allowed_communications=allowed_to_receive_from or [],
        )
        self._trusted_participants[identity] = participant
        self.gateway.register_participant(participant)
        return participant

    def can_communicate_with(self, sender: str, recipient: str) -> bool:
        """Check if sender has permission to communicate with recipient."""
        return self.gateway.verify_communication_permission(sender, recipient)

    def register_communication(self, sender: str, recipient: str) -> dict:
        """Register that sender can communicate with recipient."""
        return self._permission_manager.register_communication(
            sender, recipient, CommunicationDirection.BIDIRECTIONAL
        )

    def revoke_participant(self, participant_id: str) -> dict:
        """Revoke a participant."""
        return self._permission_manager.revoke_participant(participant_id)

    def is_participant_revoked(self, participant_id: str) -> bool:
        """Check if a participant is revoked."""
        return self._permission_manager.is_revoked(participant_id)

    def create_message(
        self,
        recipient: str,
        content: str,
        data_type: str = "json",
        ttl: Optional[int] = None,
    ) -> Message:
        """Create a signed message ready to send."""
        signer_id = self.gateway.get_signer_id()
        content_hash = self.gateway.compute_message_hash(content)
        timestamp = hashlib.sha256(
            f"{signer_id}{recipient}{content}".encode()
        ).hexdigest()[:16]
        message_id = f"msg_{timestamp}"

        signature = self.gateway.sign(f"{content_hash}{recipient}", signer_id)

        return Message(
            sender=signer_id,
            recipient=recipient,
            content=content,
            content_hash=content_hash,
            signature=signature,
            timestamp=timestamp,
            message_id=message_id,
            data_type=data_type,
        )

    def verify_message(self, message: Message) -> bool:
        """Verify a complete message (signature + integrity)."""
        data_to_verify = f"{message.content_hash}{message.recipient}"

        if not self.gateway.verify_signature(
            data_to_verify, message.signature, message.sender
        ):
            logger.error(f"[FabricSecurity] Invalid signature from {message.sender}")
            return False

        if not self.gateway.verify_message_integrity(
            message.content, message.content_hash
        ):
            logger.error(f"[FabricSecurity] Message altered")
            return False

        return True

    def assert_message_valid(self, message: Message):
        """Raise exception if message is not valid."""
        if not self.verify_message(message):
            raise SignatureError(f"Invalid message from {message.sender}")

    def master_audit(
        self,
        task_prefix: str,
        trusted_slaves: list,
        collection: str = "assetCollection",
    ):
        """Decorator for Master functions with complete audit."""
        return base_master_audit(task_prefix, trusted_slaves, collection)

    def slave_verify(
        self,
        trusted_masters: list,
        collection: str = "assetCollection",
    ):
        """Decorator for Slave functions with Zero Trust verification."""
        return base_slave_verify(trusted_masters, collection)

    def get_stats(self) -> dict:
        """Get statistics."""
        return {
            "identity": self.get_signer_id(),
            "using_fabric": self.is_using_fabric(),
            "rate_limiter": self._rate_limiter.get_stats(),
            "storage": self.gateway.local_storage.get_stats(),
            "revoked_count": len(self._permission_manager.get_revoked_participants()),
        }


class FabricSecuritySimple:
    """
    Simplified version of FabricSecurity for basic use cases.
    Does not include all Zero Trust validations but is easier to use.
    """

    def __init__(
        self,
        me: str,
        peer_url: Optional[str] = None,
        msp_path: Optional[str] = None,
    ):
        """Initialize FabricSecuritySimple."""
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

    def get_signer_id(self) -> str:
        """Get current signer identity."""
        return self.gateway.get_signer_id()

    def get_signer_cn(self) -> str:
        """Get current signer Common Name."""
        return self.gateway.get_signer_cn()

    def is_using_fabric(self) -> bool:
        """Check if using Fabric backend."""
        return self.gateway.is_using_fabric

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

    def register_identity(self) -> dict:
        """Register identity."""
        return self.gateway.register_certificate()

    def register_code(self, code_paths: list, version: str = "1.0.0") -> dict:
        """Register code."""
        return self.gateway.register_code_identity(code_paths, version)

    def create_message(
        self,
        sender: str = None,
        recipient: str = None,
        content: str = None,
        data_type: str = "json",
    ) -> "Message":
        """Create a signed message ready to send."""
        from .core import Message

        signer_id = sender or self.gateway.get_signer_id()
        content_hash = self.gateway.compute_message_hash(content or "")
        timestamp = hashlib.sha256(
            f"{signer_id}{recipient or ''}{content or ''}".encode()
        ).hexdigest()[:16]
        message_id = f"msg_{timestamp}"

        signature = self.gateway.sign(f"{content_hash}{recipient or ''}", signer_id)

        return Message(
            sender=signer_id,
            recipient=recipient or "",
            content=content or "",
            content_hash=content_hash,
            signature=signature,
            timestamp=timestamp,
            message_id=message_id,
            data_type=data_type,
        )

    def verify_message(self, message: "Message") -> bool:
        """Verify a complete message (signature + integrity)."""
        data_to_verify = f"{message.content_hash}{message.recipient}"

        if not self.gateway.verify_signature(
            data_to_verify, message.signature, message.sender
        ):
            logger.error(
                f"[FabricSecuritySimple] Invalid signature from {message.sender}"
            )
            return False

        if not self.gateway.verify_message_integrity(
            message.content, message.content_hash
        ):
            logger.error(f"[FabricSecuritySimple] Message altered")
            return False

        return True

    def verify_code(self, code_paths: list = None) -> bool:
        """Verify code."""
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
        """Decorator for Master functions."""

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
                            f"[Master {signer_id}] Unauthorized slave: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise SignatureError("Invalid slave signature.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completed")
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
                            f"[Master {signer_id}] Unauthorized slave: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise SignatureError("Invalid slave signature.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completed")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator

    def slave_verify(
        self,
        trusted_masters: list,
        collection: str = "assetCollection",
    ):
        """Decorator for Slave functions."""

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
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} not verified, continuing..."
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

                    logger.info(f"[Slave {signer_id}] Task {t_id} completed")
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
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} not verified, continuing..."
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

                    logger.info(f"[Slave {signer_id}] Task {t_id} completed")
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


__all__ = [
    "FabricSecurity",
    "FabricSecuritySimple",
    "FabricGateway",
    "FabricNetwork",
    "FabricContract",
    "SecurityError",
    "CodeIntegrityError",
    "PermissionDeniedError",
    "MessageIntegrityError",
    "SignatureError",
    "RateLimitError",
    "RevocationError",
    "CommunicationDirection",
    "Participant",
    "Message",
    "RateLimiter",
    "with_retry",
    "HashingService",
    "SigningService",
    "IdentityManager",
]
