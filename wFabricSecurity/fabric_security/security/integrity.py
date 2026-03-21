"""Code integrity verification for wFabricSecurity."""

import traceback
import logging
from pathlib import Path
from typing import List, Optional, Union

from ..core.exceptions import CodeIntegrityError
from ..crypto.hashing import HashingService

logger = logging.getLogger("FabricSecurity.Integrity")


class IntegrityVerifier:
    """Verifies code integrity using hashes."""

    def __init__(self, gateway: "FabricGateway"):
        """Initialize integrity verifier.

        Args:
            gateway: Fabric Gateway instance
        """
        self._gateway = gateway
        self._hashing = HashingService()

    def compute_code_hash(self, code_paths: List[Union[str, Path]]) -> str:
        """Compute hash of code files.

        Args:
            code_paths: List of file or directory paths

        Returns:
            SHA-256 hash prefixed with 'sha256:'
        """
        return self._hashing.compute_code_hash(code_paths)

    def verify_code_integrity(
        self,
        code_paths: List[Union[str, Path]],
        registered_hash: Optional[str] = None,
    ) -> bool:
        """Verify that code matches registered hash.

        Args:
            code_paths: Paths to code files
            registered_hash: Expected hash (from Fabric)

        Returns:
            True if code is unchanged

        Raises:
            CodeIntegrityError: If code has been tampered with
        """
        current_hash = self.compute_code_hash(code_paths)

        if registered_hash:
            if current_hash != registered_hash:
                raise CodeIntegrityError(
                    message="Code integrity verification failed. Code has been modified.",
                    details={
                        "current_hash": current_hash,
                        "registered_hash": registered_hash,
                        "code_paths": [str(p) for p in code_paths],
                    },
                )
            logger.info("Code integrity verified successfully")
            return True

        signer_id = self._gateway.get_signer_id()
        participant_data = None

        if self._gateway.is_using_fabric:
            participant_data = self._gateway.fabric_storage.get_participant(signer_id)

        if not participant_data:
            participant_data = self._gateway.local_storage.get(
                f"participant_{signer_id}"
            )

        if participant_data and participant_data.get("code_hash"):
            reg_hash = participant_data["code_hash"]
            if current_hash != reg_hash:
                raise CodeIntegrityError(
                    message="Code integrity verification failed. Code has been modified.",
                    details={
                        "current_hash": current_hash,
                        "registered_hash": reg_hash,
                        "code_paths": [str(p) for p in code_paths],
                    },
                )
            logger.info("Code integrity verified against registered hash")
            return True

        logger.warning("No registered hash found, skipping verification")
        return True

    def verify_own_code(self, caller_frame_depth: int = 2) -> bool:
        """Verify integrity of calling code.

        Args:
            caller_frame_depth: Stack depth to find calling file

        Returns:
            True if code is valid

        Raises:
            CodeIntegrityError: If code has been tampered with
        """
        stack = traceback.extract_stack()
        if len(stack) > caller_frame_depth:
            caller_frame = stack[-caller_frame_depth]
            code_paths = [caller_frame.filename]
            return self.verify_code_integrity(code_paths)
        return True

    def register_code(
        self,
        code_paths: List[Union[str, Path]],
        version: str = "1.0.0",
    ) -> dict:
        """Register code hash in Fabric.

        Args:
            code_paths: Paths to code files
            version: Code version

        Returns:
            Registration result
        """
        return self._gateway.register_code_identity(code_paths, version)

    def get_registered_hash(self, identity: Optional[str] = None) -> Optional[str]:
        """Get registered hash for an identity.

        Args:
            identity: Identity to check (defaults to current)

        Returns:
            Registered hash or None
        """
        if identity is None:
            identity = self._gateway.get_signer_id()

        if self._gateway.is_using_fabric:
            participant = self._gateway.fabric_storage.get_participant(identity)
            if participant:
                return participant.get("code_hash")

        participant = self._gateway.local_storage.get(f"participant_{identity}")
        if participant:
            return participant.get("code_hash")

        return None

    def verify_multiple_paths(
        self,
        paths_and_hashes: List[tuple],
    ) -> List[bool]:
        """Verify multiple code paths against expected hashes.

        Args:
            paths_and_hashes: List of (path, expected_hash) tuples

        Returns:
            List of verification results
        """
        results = []
        for path, expected_hash in paths_and_hashes:
            try:
                result = self.verify_code_integrity([path], expected_hash)
                results.append(result)
            except CodeIntegrityError:
                results.append(False)
        return results
