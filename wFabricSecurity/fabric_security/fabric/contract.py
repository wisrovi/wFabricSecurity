"""Fabric Contract for wFabricSecurity."""

import json
import logging
from typing import Any, List, Optional

logger = logging.getLogger("FabricSecurity.Contract")


class FabricContract:
    """Represents a Fabric chaincode contract."""

    def __init__(
        self,
        gateway: "FabricGateway",
        channel: str,
        chaincode: str,
    ):
        """Initialize Fabric Contract.

        Args:
            gateway: Fabric Gateway instance
            channel: Channel name
            chaincode: Chaincode name
        """
        self._gateway = gateway
        self._channel = channel
        self._chaincode = chaincode

    @property
    def channel(self) -> str:
        """Get channel name."""
        return self._channel

    @property
    def chaincode(self) -> str:
        """Get chaincode name."""
        return self._chaincode

    def submit_transaction(
        self,
        function: str,
        *args: Any,
    ) -> dict:
        """Submit a transaction to the chaincode.

        Args:
            function: Function name
            *args: Function arguments

        Returns:
            Result dictionary
        """
        str_args = [str(arg) for arg in args]
        return self._gateway.invoke_chaincode(function, *str_args)

    def evaluate_transaction(
        self,
        function: str,
        *args: Any,
    ) -> Optional[str]:
        """Evaluate a transaction (query).

        Args:
            function: Function name
            *args: Function arguments

        Returns:
            Query result or None
        """
        str_args = [str(arg) for arg in args]
        return self._gateway.query_chaincode(function, *str_args)

    def register_certificate(self, signer_id: str, cert_pem: str) -> dict:
        """Register a certificate."""
        return self.submit_transaction("RegisterCertificate", signer_id, cert_pem)

    def get_certificate(self, signer_id: str) -> Optional[str]:
        """Get a certificate."""
        return self.evaluate_transaction("GetCertificate", signer_id)

    def register_participant(self, participant_data: dict) -> dict:
        """Register a participant."""
        data_json = json.dumps(participant_data)
        return self.submit_transaction(
            "RegisterParticipant", participant_data["identity"], data_json
        )

    def get_participant(self, identity: str) -> Optional[dict]:
        """Get a participant."""
        result = self.evaluate_transaction("GetParticipant", identity)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass
        return None

    def register_task(self, task_id: str, hash_a: str) -> dict:
        """Register a task."""
        return self.submit_transaction("RegisterTask", task_id, hash_a)

    def complete_task(self, task_id: str, hash_b: str) -> dict:
        """Complete a task."""
        return self.submit_transaction("CompleteTask", task_id, hash_b)

    def get_task(self, task_id: str) -> Optional[dict]:
        """Get a task."""
        result = self.evaluate_transaction("GetTask", task_id)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass
        return None

    def put_private_data(
        self,
        collection: str,
        key: str,
        value: Any,
    ) -> dict:
        """Put private data."""
        value_json = json.dumps(value)
        return self.submit_transaction("PutPrivateData", collection, key, value_json)

    def get_private_data(
        self,
        collection: str,
        key: str,
    ) -> Optional[Any]:
        """Get private data."""
        result = self.evaluate_transaction("GetPrivateData", collection, key)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return None

    def create_task_with_payload(
        self,
        task_id: str,
        hash_a: str,
        payload: dict,
        collection: str = "assetCollection",
    ) -> dict:
        """Create a task with private payload.

        Args:
            task_id: Task ID
            hash_a: Input hash
            payload: Private payload data
            collection: Private collection name

        Returns:
            Result dictionary
        """
        register_result = self.register_task(task_id, hash_a)
        if register_result.get("status") == "success":
            put_result = self.put_private_data(collection, task_id, payload)
            return {"status": "success", "task": register_result, "payload": put_result}
        return register_result

    def get_task_with_payload(
        self,
        task_id: str,
        collection: str = "assetCollection",
    ) -> Optional[dict]:
        """Get a task with its private payload.

        Args:
            task_id: Task ID
            collection: Private collection name

        Returns:
            Task data with payload or None
        """
        task = self.get_task(task_id)
        if task:
            payload = self.get_private_data(collection, task_id)
            task["_payload"] = payload
        return task
