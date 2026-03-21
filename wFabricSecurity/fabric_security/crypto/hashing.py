"""Hashing utilities for wFabricSecurity."""

import hashlib
from pathlib import Path
from typing import List, Union


class HashingService:
    """Service for computing various hashes used in the system."""

    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """Compute SHA-256 hash of data.

        Args:
            data: String or bytes to hash

        Returns:
            Hex digest prefixed with 'sha256:'
        """
        if isinstance(data, str):
            data = data.encode()
        return f"sha256:{hashlib.sha256(data).hexdigest()}"

    @staticmethod
    def sha256_raw(data: Union[str, bytes]) -> str:
        """Compute raw SHA-256 hash (no prefix).

        Args:
            data: String or bytes to hash

        Returns:
            Hex digest without prefix
        """
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_message_hash(content: str) -> str:
        """Compute hash of a message.

        Args:
            content: Message content string

        Returns:
            Hash prefixed with 'sha256:'
        """
        return HashingService.sha256(content)

    @staticmethod
    def compute_code_hash(code_paths: List[Union[str, Path]]) -> str:
        """Compute SHA-256 hash of one or more code files.

        Args:
            code_paths: List of file or directory paths to hash

        Returns:
            Combined hash prefixed with 'sha256:'
        """
        hasher = hashlib.sha256()

        for code_path in sorted(code_paths, key=lambda p: str(p)):
            path = Path(code_path)
            if path.is_file():
                hasher.update(f"FILE:{path.name}".encode())
                with open(path, "rb") as f:
                    hasher.update(f.read())
            elif path.is_dir():
                for file_path in sorted(path.rglob("*.py")):
                    relative = file_path.relative_to(path)
                    hasher.update(f"FILE:{relative}".encode())
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())

        return f"sha256:{hasher.hexdigest()}"

    @staticmethod
    def compute_file_hash(file_path: Union[str, Path]) -> str:
        """Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hash prefixed with 'sha256:'
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return f"sha256:{hasher.hexdigest()}"

    @staticmethod
    def verify_hash(data: Union[str, bytes], expected_hash: str) -> bool:
        """Verify that data matches expected hash.

        Args:
            data: Data to verify
            expected_hash: Expected hash (with or without prefix)

        Returns:
            True if hash matches
        """
        actual = HashingService.sha256(data)
        if expected_hash.startswith("sha256:"):
            return actual == expected_hash
        return actual == f"sha256:{expected_hash}"

    @staticmethod
    def compute_multihash(data: Union[str, bytes], *hash_names: str) -> dict:
        """Compute multiple hashes of data.

        Args:
            data: Data to hash
            *hash_names: Names of hash algorithms ('sha256', 'sha512', 'md5')

        Returns:
            Dictionary mapping hash name to hash value
        """
        if isinstance(data, str):
            data = data.encode()

        result = {}
        for name in hash_names:
            name_lower = name.lower()
            if name_lower == "sha256":
                hasher = hashlib.sha256(data)
                result["sha256"] = hasher.hexdigest()
            elif name_lower == "sha512":
                hasher = hashlib.sha512(data)
                result["sha512"] = hasher.hexdigest()
            elif name_lower == "md5":
                hasher = hashlib.md5(data)
                result["md5"] = hasher.hexdigest()
            elif name_lower == "blake2b":
                hasher = hashlib.blake2b(data)
                result["blake2b"] = hasher.hexdigest()
            elif name_lower == "blake2s":
                hasher = hashlib.blake2s(data)
                result["blake2s"] = hasher.hexdigest()

        return result
