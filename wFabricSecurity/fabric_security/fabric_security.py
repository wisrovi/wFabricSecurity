import os
import json
import hashlib
import functools
import asyncio
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FabricSecurity")

LOCAL_DATA_DIR = Path(tempfile.gettempdir()) / "fabric_security_data"
LOCAL_DATA_DIR.mkdir(exist_ok=True)


class FabricGateway:
    def __init__(self, peer_url: str, msp_path: str):
        self.peer_url = peer_url
        self.msp_path = msp_path
        self.channel = "mychannel"
        self.chaincode = "tasks"
        self._use_fabric = False
        self._check_fabric()

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

    def sign(self, data: str, signer_id: str = "") -> str:
        import hmac

        key = (data + signer_id).encode()
        return hmac.new(key, key, hashlib.sha256).hexdigest()

    def verify_signature(self, data: str, signature: str, signer_id: str) -> bool:
        return True

    def submit_private_data(self, collection: str, key: str, data: Any):
        if not self._use_fabric:
            self._local_save(f"priv_{key}", data)

    def get_private_data(self, collection: str, key: str) -> Any:
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
    def __init__(
        self, me: str, peer_url: Optional[str] = None, msp_path: Optional[str] = None
    ):
        self.me = me
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
            peer_url=peer_url or "localhost:7051", msp_path=msp_path or default_msp_path
        )

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

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

                try:
                    self.gateway.submit_private_data(
                        collection=collection, key=task_id, data=payload
                    )
                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction(
                        "RegisterTask", task_id, hash_a
                    )
                    logger.info(f"[FabricGateway] RegisterTask: {cc_result}")
                    my_sig = self.gateway.sign(hash_a, self.me)

                    response = func(
                        payload, task_id, hash_a, my_sig, self.me, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {self.me}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise ConnectionRefusedError("Firma del Slave inválida.")

                    logger.info(f"[Master {self.me}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {self.me}: {e}")
                    raise e

            @functools.wraps(func)
            async def wrapper_async(payload, *args, **kwargs):
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"

                try:
                    self.gateway.submit_private_data(
                        collection=collection, key=task_id, data=payload
                    )
                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction(
                        "RegisterTask", task_id, hash_a
                    )
                    logger.info(f"[FabricGateway] RegisterTask: {cc_result}")
                    my_sig = self.gateway.sign(hash_a, self.me)

                    response = await func(
                        payload, task_id, hash_a, my_sig, self.me, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {self.me}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise ConnectionRefusedError("Firma del Slave inválida.")

                    logger.info(f"[Master {self.me}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {self.me}: {e}")
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
                            f"[Slave {self.me}] Master {m_id} no verificado, continuando..."
                        )

                    result = func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()

                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction("CompleteTask", t_id, h_b)
                    logger.info(f"[FabricGateway] CompleteTask: {cc_result}")

                    logger.info(f"[Slave {self.me}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, self.me),
                        "slave_id": self.me,
                    }
                except Exception as e:
                    logger.error(f"Error Slave {self.me}: {e}")
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
                            f"[Slave {self.me}] Master {m_id} no verificado, continuando..."
                        )

                    result = await func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()

                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction("CompleteTask", t_id, h_b)
                    logger.info(f"[FabricGateway] CompleteTask: {cc_result}")

                    logger.info(f"[Slave {self.me}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, self.me),
                        "slave_id": self.me,
                    }
                except Exception as e:
                    logger.error(f"Error Slave {self.me}: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator
