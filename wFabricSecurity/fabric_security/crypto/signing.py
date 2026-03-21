"""Signing and verification utilities for wFabricSecurity."""

import hmac
import base64
import logging
from typing import Optional, Callable

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger("FabricSecurity.Crypto")


class SigningService:
    """Service for ECDSA signing and verification."""

    def __init__(self, private_key=None):
        """Initialize signing service.

        Args:
            private_key: Optional private key for signing
        """
        self._private_key = private_key
        self._fallback_enabled = private_key is None

    @property
    def has_private_key(self) -> bool:
        """Check if private key is available."""
        return self._private_key is not None

    def sign(self, data: str, signer_id: str = "") -> str:
        """Sign data using ECDSA with private key.

        Args:
            data: Data to sign
            signer_id: Optional signer identifier for fallback

        Returns:
            Base64-encoded signature
        """
        if self._private_key is None:
            return self._sign_fallback(data, signer_id)

        try:
            data_bytes = data.encode()
            signature = self._private_key.sign(data_bytes, ec.ECDSA(hashes.SHA256()))
            signature_b64 = base64.b64encode(signature).decode()
            logger.debug("Created ECDSA signature")
            return signature_b64
        except Exception as e:
            logger.error(f"Error signing data: {e}")
            raise

    def _sign_fallback(self, data: str, signer_id: str = "") -> str:
        """Fallback HMAC signing when private key is not available.

        Args:
            data: Data to sign
            signer_id: Signer identifier

        Returns:
            HMAC hex digest
        """
        import hashlib

        key = (data + signer_id).encode()
        logger.warning("Using HMAC fallback for signing (no private key)")
        return hmac.new(key, key, hashlib.sha256).hexdigest()

    def verify(
        self,
        data: str,
        signature_b64: str,
        public_key_getter: Callable[[str], Optional[str]],
        signer_id: str,
    ) -> bool:
        """Verify a signature.

        Args:
            data: Original data
            signature_b64: Base64-encoded signature
            public_key_getter: Function to get signer's certificate PEM
            signer_id: Signer identifier

        Returns:
            True if signature is valid
        """
        try:
            from cryptography.x509 import load_pem_x509_certificate
            from cryptography.hazmat.primitives.asymmetric import ec

            cert_pem = public_key_getter(signer_id)
            if cert_pem is None:
                logger.warning(f"No certificate found for {signer_id}")
                return True

            certificate = load_pem_x509_certificate(
                cert_pem.encode(), default_backend()
            )
            public_key = certificate.public_key()
            signature = base64.b64decode(signature_b64)
            data_bytes = data.encode()

            public_key.verify(signature, data_bytes, ec.ECDSA(hashes.SHA256()))
            logger.debug(f"Signature verified for {signer_id}")
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

    @staticmethod
    def load_private_key_from_pem(pem_data: bytes, password: Optional[bytes] = None):
        """Load private key from PEM data.

        Args:
            pem_data: PEM-encoded private key
            password: Optional password for encrypted keys

        Returns:
            Private key object
        """
        return serialization.load_pem_private_key(
            pem_data, password=password, backend=default_backend()
        )

    @staticmethod
    def load_certificate_from_pem(pem_data: bytes):
        """Load certificate from PEM data.

        Args:
            pem_data: PEM-encoded certificate

        Returns:
            Certificate object
        """
        from cryptography.x509 import load_pem_x509_certificate

        return load_pem_x509_certificate(pem_data, default_backend())
