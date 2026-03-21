"""Fabric blockchain storage for wFabricSecurity."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, List, Optional, Tuple

logger = logging.getLogger("FabricSecurity.FabricStorage")


class FabricStorage:
    """Storage operations using Hyperledger Fabric as backend."""

    def __init__(
        self,
        channel: str = "mychannel",
        chaincode: str = "tasks",
        cli_container: str = "cli",
        orderer_url: str = "orderer.net:7050",
        tls_enabled: bool = False,
        tls_ca_file: str = "/etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem",
    ):
        """Initialize Fabric storage.

        Args:
            channel: Fabric channel name
            chaincode: Chaincode name
            cli_container: Docker container name for CLI
            orderer_url: Orderer URL
            tls_enabled: Whether TLS is enabled
            tls_ca_file: TLS CA file path
        """
        self.channel = channel
        self.chaincode = chaincode
        self.cli_container = cli_container
        self.orderer_url = orderer_url
        self.tls_enabled = tls_enabled
        self.tls_ca_file = tls_ca_file
        self._available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """Check if Fabric is available."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={self.cli_container}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if self.cli_container in result.stdout:
                self._available = True
                logger.info("Fabric storage available")
            else:
                logger.warning("Fabric CLI container not running")
        except Exception as e:
            logger.warning(f"Failed to check Fabric availability: {e}")

    @property
    def is_available(self) -> bool:
        """Check if Fabric storage is available."""
        return self._available

    def _run_cli(self, args: List[str], timeout: int = 60) -> Tuple[bool, str]:
        """Run a command in the Fabric CLI container.

        Args:
            args: Command arguments
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, output)
        """
        cmd = ["docker", "exec", self.cli_container, "peer"] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def invoke(
        self,
        function: str,
        *args: str,
        wait_for_event: bool = True,
    ) -> dict:
        """Invoke a chaincode function.

        Args:
            function: Chaincode function name
            *args: Function arguments
            wait_for_event: Whether to wait for event

        Returns:
            Result dictionary with status and tx_id
        """
        import hashlib

        args_str = json.dumps({"Args": [function] + list(args)})
        cmd_args = [
            "chaincode",
            "invoke",
            "-C",
            self.channel,
            "-n",
            self.chaincode,
            "-c",
            args_str,
            "-o",
            self.orderer_url,
        ]

        if not self.tls_enabled:
            cmd_args.extend(["--tls=false"])
        else:
            cmd_args.extend(["--cafile", self.tls_ca_file])

        if wait_for_event:
            cmd_args.append("--waitForEvent")

        success, output = self._run_cli(cmd_args, timeout=90)
        tx_id = hashlib.sha256(str(args).encode()).hexdigest()[:12]

        if success:
            logger.info(f"Fabric invoke {function}({args}) -> SUCCESS (tx: {tx_id})")
            return {"status": "success", "tx_id": tx_id}
        else:
            logger.warning(
                f"Fabric invoke {function}({args}) -> FAILED: {output[:200]}"
            )
            return {"status": "failed", "tx_id": tx_id, "error": output[:200]}

    def query(self, function: str, *args: str) -> Optional[str]:
        """Query a chaincode function.

        Args:
            function: Chaincode function name
            *args: Function arguments

        Returns:
            Query result or None
        """
        args_str = json.dumps({"Args": [function] + list(args)})
        success, output = self._run_cli(
            [
                "chaincode",
                "query",
                "-C",
                self.channel,
                "-n",
                self.chaincode,
                "-c",
                args_str,
            ]
        )

        if success and "Error:" not in output:
            return output.strip()
        return None

    def register_certificate(self, signer_id: str, cert_pem: str) -> dict:
        """Register a certificate in Fabric.

        Args:
            signer_id: Signer identity
            cert_pem: PEM-encoded certificate

        Returns:
            Result dictionary
        """
        return self.invoke("RegisterCertificate", signer_id, cert_pem)

    def get_certificate(self, signer_id: str) -> Optional[str]:
        """Get a certificate from Fabric.

        Args:
            signer_id: Signer identity

        Returns:
            Certificate PEM or None
        """
        return self.query("GetCertificate", signer_id)

    def register_participant(self, participant_data: dict) -> dict:
        """Register a participant in Fabric.

        Args:
            participant_data: Participant data dictionary

        Returns:
            Result dictionary
        """
        import base64

        participant_json = json.dumps(participant_data)
        participant_b64 = base64.b64encode(participant_json.encode()).decode()
        return self.invoke(
            "RegisterParticipant", participant_data["identity"], participant_b64
        )

    def get_participant(self, identity: str) -> Optional[dict]:
        """Get a participant from Fabric.

        Args:
            identity: Participant identity

        Returns:
            Participant data or None
        """
        import base64

        result = self.query("GetParticipant", identity)
        if result:
            try:
                participant_b64 = result.strip()
                participant_json = base64.b64decode(participant_b64).decode()
                return json.loads(participant_json)
            except Exception as e:
                logger.warning(f"Failed to decode participant: {e}")
        return None

    def register_task(self, task_id: str, hash_a: str) -> dict:
        """Register a task in Fabric.

        Args:
            task_id: Task ID
            hash_a: Hash of input

        Returns:
            Result dictionary
        """
        return self.invoke("RegisterTask", task_id, hash_a)

    def complete_task(self, task_id: str, hash_b: str) -> dict:
        """Mark a task as completed in Fabric.

        Args:
            task_id: Task ID
            hash_b: Hash of output

        Returns:
            Result dictionary
        """
        return self.invoke("CompleteTask", task_id, hash_b)

    def get_task(self, task_id: str) -> Optional[dict]:
        """Get a task from Fabric.

        Args:
            task_id: Task ID

        Returns:
            Task data or None
        """
        result = self.query("GetTask", task_id)
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
        """Put private data in Fabric.

        Args:
            collection: Private collection name
            key: Data key
            value: Data value

        Returns:
            Result dictionary
        """
        return self.invoke("PutPrivateData", collection, key, json.dumps(value))

    def get_private_data(
        self,
        collection: str,
        key: str,
    ) -> Optional[Any]:
        """Get private data from Fabric.

        Args:
            collection: Private collection name
            key: Data key

        Returns:
            Data or None
        """
        result = self.query("GetPrivateData", collection, key)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return None

    def test_connection(self) -> bool:
        """Test connection to Fabric.

        Returns:
            True if connection works
        """
        result = self.query("GetTask", "__test__")
        return result is not None
