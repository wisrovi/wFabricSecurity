"""Identity management for wFabricSecurity."""

import os
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

logger = logging.getLogger("FabricSecurity.Identity")


class CachedCertificate:
    """Wrapper for cached certificate with TTL."""

    def __init__(self, cert_pem: str, expires_at: datetime):
        self.cert_pem = cert_pem
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class IdentityManager:
    """Manages identity and certificates."""

    def __init__(
        self,
        msp_path: str,
        cache_size: int = 100,
        cache_ttl_seconds: int = 3600,
    ):
        """Initialize identity manager.

        Args:
            msp_path: Path to MSP directory
            cache_size: Max number of certificates to cache
            cache_ttl_seconds: TTL for cached certificates
        """
        self.msp_path = msp_path
        self._private_key = None
        self._certificate = None
        self._cache_size = cache_size
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cert_cache: dict[str, CachedCertificate] = {}
        self._load_identity()

    def _load_identity(self) -> None:
        """Load private key and certificate from MSP."""
        keystore_dir = Path(self.msp_path) / "keystore"
        signcerts_dir = Path(self.msp_path) / "signcerts"

        try:
            key_files = list(keystore_dir.glob("*"))
            if key_files:
                with open(key_files[0], "rb") as f:
                    self._private_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
                logger.info(f"Loaded private key: {key_files[0].name}")

            cert_files = list(signcerts_dir.glob("*.pem"))
            if cert_files:
                with open(cert_files[0], "rb") as f:
                    self._certificate = load_pem_x509_certificate(
                        f.read(), default_backend()
                    )
                logger.info(f"Loaded certificate: {cert_files[0].name}")
        except Exception as e:
            logger.warning(f"Failed to load identity: {e}")

    @property
    def private_key(self):
        """Get private key."""
        return self._private_key

    @property
    def certificate(self):
        """Get certificate."""
        return self._certificate

    def get_certificate_pem(self) -> Optional[str]:
        """Get PEM-encoded certificate.

        Returns:
            PEM string or None
        """
        if self._certificate:
            return self._certificate.public_bytes(serialization.Encoding.PEM).decode()
        return None

    def get_signer_id(self) -> str:
        """Get full RFC4514 string identity.

        Returns:
            Identity string from certificate subject
        """
        if self._certificate:
            return self._certificate.subject.rfc4514_string()
        return "Unknown"

    def get_signer_cn(self) -> str:
        """Get Common Name (CN) from certificate.

        Returns:
            CN value or 'Unknown'
        """
        if self._certificate:
            for attr in self._certificate.subject:
                if attr.oid == (2, 5, 4, 3):
                    return attr.value
        return "Unknown"

    def get_signer_ou(self) -> str:
        """Get Organizational Unit (OU) from certificate.

        Returns:
            OU value or 'Unknown'
        """
        if self._certificate:
            for attr in self._certificate.subject:
                if attr.oid == (2, 5, 4, 11):
                    return attr.value
        return "Unknown"

    def get_signer_org(self) -> str:
        """Get Organization (O) from certificate.

        Returns:
            O value or 'Unknown'
        """
        if self._certificate:
            for attr in self._certificate.subject:
                if attr.oid == (2, 5, 4, 10):
                    return attr.value
        return "Unknown"

    def cache_certificate(self, signer_id: str, cert_pem: str) -> None:
        """Cache a certificate.

        Args:
            signer_id: Signer identifier
            cert_pem: PEM-encoded certificate
        """
        expires_at = datetime.now() + self._cache_ttl
        self._cert_cache[signer_id] = CachedCertificate(cert_pem, expires_at)

        if len(self._cert_cache) > self._cache_size:
            oldest = min(self._cert_cache.items(), key=lambda x: x[1].expires_at)
            del self._cert_cache[oldest[0]]

    def get_cached_certificate(self, signer_id: str) -> Optional[str]:
        """Get cached certificate if not expired.

        Args:
            signer_id: Signer identifier

        Returns:
            Cached certificate PEM or None
        """
        cached = self._cert_cache.get(signer_id)
        if cached and not cached.is_expired():
            return cached.cert_pem
        if cached:
            del self._cert_cache[signer_id]
        return None

    def clear_cache(self) -> None:
        """Clear the certificate cache."""
        self._cert_cache.clear()

    def load_private_key(self, key_path: str) -> None:
        """Load private key from file.

        Args:
            key_path: Path to private key file
        """
        with open(key_path, "rb") as f:
            self._private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        logger.info(f"Loaded private key from: {key_path}")

    def load_certificate(self, cert_path: str) -> None:
        """Load certificate from file.

        Args:
            cert_path: Path to certificate file
        """
        with open(cert_path, "rb") as f:
            self._certificate = load_pem_x509_certificate(f.read(), default_backend())
        logger.info(f"Loaded certificate from: {cert_path}")

    @staticmethod
    def extract_common_name(cert_pem: str) -> Optional[str]:
        """Extract CN from certificate PEM.

        Args:
            cert_pem: PEM-encoded certificate

        Returns:
            CN value or None
        """
        try:
            cert = load_pem_x509_certificate(cert_pem.encode(), default_backend())
            for attr in cert.subject:
                if attr.oid == (2, 5, 4, 3):
                    return attr.value
        except Exception as e:
            logger.warning(f"Failed to extract CN: {e}")
        return None

    @staticmethod
    def extract_public_key_pem(cert_pem: str) -> Optional[str]:
        """Extract public key from certificate.

        Args:
            cert_pem: PEM-encoded certificate

        Returns:
            PEM-encoded public key or None
        """
        try:
            cert = load_pem_x509_certificate(cert_pem.encode(), default_backend())
            public_key = cert.public_key()
            return public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()
        except Exception as e:
            logger.warning(f"Failed to extract public key: {e}")
        return None
