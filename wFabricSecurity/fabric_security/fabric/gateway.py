"""Fabric Gateway for wFabricSecurity."""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Any

from ..crypto.identity import IdentityManager
from ..crypto.hashing import HashingService
from ..crypto.signing import SigningService
from ..storage.local import LocalStorage
from ..storage.fabric_storage import FabricStorage

logger = logging.getLogger("FabricSecurity.Gateway")


class FabricGateway:
    """Gateway for communication with Hyperledger Fabric."""

    def __init__(
        self,
        peer_url: str = "localhost:7051",
        msp_path: str = "",
        channel: str = "mychannel",
        chaincode: str = "tasks",
        local_storage_dir: Optional[str] = None,
    ):
        """Initialize Fabric Gateway.

        Args:
            peer_url: Fabric peer URL
            msp_path: Path to MSP directory
            channel: Fabric channel name
            chaincode: Chaincode name
            local_storage_dir: Directory for local fallback storage
        """
        self.peer_url = peer_url
        self.channel = channel
        self.chaincode = chaincode

        if not msp_path:
            msp_path = os.environ.get("FABRIC_MSP_PATH", "")
            if not msp_path:
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

        self._identity = IdentityManager(msp_path)
        self._signing = SigningService(self._identity.private_key)
        self._hashing = HashingService()
        self._local_storage = LocalStorage(local_storage_dir)
        self._fabric_storage = FabricStorage(
            channel=channel,
            chaincode=chaincode,
        )
        self._use_fabric = self._fabric_storage.is_available

        logger.info(
            f"FabricGateway initialized: fabric={self._use_fabric}, identity={self.get_signer_id()}"
        )

    @property
    def identity(self) -> IdentityManager:
        """Get identity manager."""
        return self._identity

    @property
    def signing(self) -> SigningService:
        """Get signing service."""
        return self._signing

    @property
    def hashing(self) -> HashingService:
        """Get hashing service."""
        return self._hashing

    @property
    def local_storage(self) -> LocalStorage:
        """Get local storage."""
        return self._local_storage

    @property
    def fabric_storage(self) -> FabricStorage:
        """Get Fabric storage."""
        return self._fabric_storage

    @property
    def is_using_fabric(self) -> bool:
        """Check if using Fabric backend."""
        return self._use_fabric

    def get_signer_id(self) -> str:
        """Get current signer identity."""
        return self._identity.get_signer_id()

    def get_signer_cn(self) -> str:
        """Get current signer Common Name."""
        return self._identity.get_signer_cn()

    def sign(self, data: str, signer_id: str = "") -> str:
        """Sign data."""
        return self._signing.sign(data, signer_id)

    def verify_signature(
        self,
        data: str,
        signature_b64: str,
        signer_id: str,
    ) -> bool:
        """Verify a signature."""

        def get_cert(sid: str) -> Optional[str]:
            if self._use_fabric:
                cert = self._fabric_storage.get_certificate(sid)
                if cert:
                    return cert
            return self._local_storage.get(f"cert_{sid}", {}).get("cert_pem")

        return self._signing.verify(data, signature_b64, get_cert, signer_id)

    def compute_code_hash(self, code_paths: list) -> str:
        """Compute hash of code files."""
        return self._hashing.compute_code_hash(code_paths)

    def compute_message_hash(self, content: str) -> str:
        """Compute hash of message content."""
        return self._hashing.compute_message_hash(content)

    def register_certificate(self) -> dict:
        """Register certificate in Fabric."""
        signer_id = self.get_signer_id()
        cert_pem = self._identity.get_certificate_pem()
        if not cert_pem:
            return {"status": "failed", "error": "No certificate available"}

        if self._use_fabric:
            result = self._fabric_storage.register_certificate(signer_id, cert_pem)
            if result.get("status") == "success":
                return result

        self._local_storage.save(f"cert_{signer_id}", {"cert_pem": cert_pem})
        return {"status": "success", "tx_id": "local"}

    def register_code_identity(
        self,
        code_paths: list,
        version: str = "1.0.0",
    ) -> dict:
        """Register code identity in Fabric."""
        code_hash = self.compute_code_hash(code_paths)
        signer_id = self.get_signer_id()

        participant_data = {
            "identity": signer_id,
            "code_hash": code_hash,
            "version": version,
            "registered_at": "",
            "allowed_communications": [],
            "direction": "bidirectional",
            "is_active": True,
        }

        if self._use_fabric:
            result = self._fabric_storage.register_participant(participant_data)
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "tx_id": result.get("tx_id", ""),
                    "code_hash": code_hash,
                    "version": version,
                }

        self._local_storage.save(f"participant_{signer_id}", participant_data)
        return {
            "status": "success",
            "tx_id": "local",
            "code_hash": code_hash,
            "version": version,
        }

    def verify_code_integrity(
        self,
        code_paths: list,
        signer_id: Optional[str] = None,
    ) -> bool:
        """Verify code integrity for a given identity."""
        from ..core.exceptions import CodeIntegrityError

        if signer_id is None:
            signer_id = self.get_signer_id()

        current_hash = self.compute_code_hash(code_paths)
        participant_data = None

        if self._use_fabric:
            participant_data = self._fabric_storage.get_participant(signer_id)

        if not participant_data:
            participant_data = self._local_storage.get(f"participant_{signer_id}")

        if participant_data and participant_data.get("code_hash"):
            if current_hash != participant_data["code_hash"]:
                raise CodeIntegrityError(
                    message="Code integrity verification failed. Code has been modified.",
                    details={
                        "current_hash": current_hash,
                        "registered_hash": participant_data["code_hash"],
                    },
                )
            return True

        logger.info("No registered code hash found, assuming valid")
        return True

    def verify_own_code_integrity(
        self,
        code_paths: list,
        registered_hash: Optional[str] = None,
    ) -> bool:
        """Verify integrity of own code."""
        return self.verify_code_integrity(code_paths, self.get_signer_id())

    def invoke_chaincode(self, func: str, *args) -> dict:
        """Invoke a chaincode function."""
        if self._use_fabric:
            return self._fabric_storage.invoke(func, *args)

        key = args[0] if args else ""
        value = args[1] if len(args) > 1 else ""
        self._local_storage.save(key, {"func": func, "value": value})
        return {"status": "success", "tx_id": "local"}

    def query_chaincode(self, func: str, *args) -> Optional[str]:
        """Query a chaincode function."""
        if self._use_fabric:
            return self._fabric_storage.query(func, *args)

        key = args[0] if args else ""
        result = self._local_storage.get(key)
        return json.dumps(result) if result else None

    def get_private_data(self, collection: str, key: str) -> Optional[Any]:
        """Get private data from Fabric."""
        if self._use_fabric:
            return self._fabric_storage.get_private_data(collection, key)
        return self._local_storage.get(f"private_{collection}_{key}")

    def get_certificate_pem(self) -> Optional[str]:
        """Get PEM-encoded certificate."""
        return self._identity.get_certificate_pem()

    def register_certificate(self) -> dict:
        """Register certificate in Fabric."""
        signer_id = self.get_signer_id()
        cert_pem = self._identity.get_certificate_pem()
        if not cert_pem:
            return {"status": "failed", "error": "No certificate available"}

        if self._use_fabric:
            result = self._fabric_storage.register_certificate(signer_id, cert_pem)
            if result.get("status") == "success":
                return result

        self._local_storage.save(f"cert_{signer_id}", {"cert_pem": cert_pem})
        return {"status": "success", "tx_id": "local"}

    def register_participant(self, participant) -> None:
        """Register a participant.

        Args:
            participant: Either a dict or Participant object
        """
        if hasattr(participant, "identity"):
            participant_dict = (
                participant.to_dict()
                if hasattr(participant, "to_dict")
                else {
                    "identity": participant.identity,
                    "code_hash": participant.code_hash,
                    "version": participant.version,
                }
            )
        else:
            participant_dict = participant
        self._local_storage.save(
            f"participant_{participant_dict['identity']}", participant_dict
        )

    def verify_communication_permission(
        self, from_identity: str, to_identity: str
    ) -> bool:
        """Verify communication permission."""
        permissions_key = f"perm_{from_identity}"
        permissions = self._local_storage.get(permissions_key)

        if permissions and to_identity in permissions.get("allowed", []):
            return True
        return False

    def verify_message_integrity(self, content: str, content_hash: str) -> bool:
        """Verify message integrity.

        Args:
            content: Message content
            content_hash: Expected hash of content

        Returns:
            True if hash matches
        """
        computed_hash = self.compute_message_hash(content)
        return computed_hash == content_hash

    def assert_message_integrity(self, content: str, content_hash: str) -> None:
        """Assert message integrity, raise if mismatch.

        Args:
            content: Message content
            content_hash: Expected hash of content

        Raises:
            MessageIntegrityError: If content hash doesn't match
        """
        from ..core.exceptions import MessageIntegrityError

        if not self.verify_message_integrity(content, content_hash):
            raise MessageIntegrityError(
                message="Message content has been modified.",
                details={
                    "expected_hash": content_hash,
                    "actual_hash": self.compute_message_hash(content),
                },
            )

    def submit_private_data(
        self,
        collection: str,
        key: str,
        value: Any,
    ) -> dict:
        """Submit private data to Fabric."""
        if self._use_fabric:
            return self._fabric_storage.put_private_data(collection, key, value)
        self._local_storage.save(f"private_{collection}_{key}", value)
        return {"status": "success", "tx_id": "local"}
