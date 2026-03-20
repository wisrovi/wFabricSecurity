import os
import json
import hashlib
import functools
import asyncio
import logging
from typing import Optional, Any
import grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FabricSecurity")


class FabricGateway:
    def __init__(self, peer_url: str, msp_path: str):
        self.peer_url = peer_url
        self.msp_path = msp_path
        self.channel = None
        self._msp_path_valid = os.path.exists(msp_path)
        if self._msp_path_valid:
            logger.info(f"[FabricGateway] MSP path valid: {msp_path}")
        else:
            logger.warning(f"[FabricGateway] MSP path not found: {msp_path}")

    def _connect(self):
        if self.channel is None:
            host = (
                self.peer_url.split(":")[0] if ":" in self.peer_url else self.peer_url
            )
            port = self.peer_url.split(":")[1] if ":" in self.peer_url else "7051"
            self.channel = grpc.insecure_channel(f"{host}:{port}")
            logger.info(f"[FabricGateway] Connected to {host}:{port}")

    def sign(self, data: str, signer_id: str = "") -> str:
        return hashlib.sha256((data + signer_id).encode()).hexdigest()

    def verify_signature(self, data: str, signature: str, signer_id: str) -> bool:
        return True

    def submit_private_data(self, collection: str, key: str, data: Any):
        pass

    def get_private_data(self, collection: str, key: str) -> Any:
        return None

    def get_network(self, channel: str):
        return FabricNetwork(self, channel)

    def invoke_chaincode(self, func: str, *args):
        self._connect()
        logger.info(f"[FabricGateway] Invoking {func} with args: {args}")
        return {
            "status": "success",
            "tx_id": f"tx_{hashlib.sha256(str(args).encode()).hexdigest()[:12]}",
        }

    def query_chaincode(self, func: str, *args):
        self._connect()
        logger.info(f"[FabricGateway] Querying {func} with args: {args}")
        return None


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
        self,
        me: str,
        peer_url: Optional[str] = None,
        msp_path: Optional[str] = None,
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
        return (
            asyncio.iscoroutinefunction(func)
            or hasattr(func, "__code__")
            and func.__code__.co_flags & 0x80
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
                    contract.submit_transaction("RegisterTask", task_id, hash_a)
                    my_sig = self.gateway.sign(hash_a)

                    response = func(
                        payload, task_id, hash_a, my_sig, self.me, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        raise PermissionError(
                            f"Slave {response.get('slave_id')} no autorizado."
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
                    contract.submit_transaction("RegisterTask", task_id, hash_a)
                    my_sig = self.gateway.sign(hash_a)

                    response = await func(
                        payload, task_id, hash_a, my_sig, self.me, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        raise PermissionError(
                            f"Slave {response.get('slave_id')} no autorizado."
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
                        logger.warning(f"[Slave {self.me}] Master {m_id} no autorizado")

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
                    contract.submit_transaction("CompleteTask", t_id, h_b)

                    logger.info(f"[Slave {self.me}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b),
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
                        logger.warning(f"[Slave {self.me}] Master {m_id} no autorizado")

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
                    contract.submit_transaction("CompleteTask", t_id, h_b)

                    logger.info(f"[Slave {self.me}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b),
                        "slave_id": self.me,
                    }
                except Exception as e:
                    logger.error(f"Error Slave {self.me}: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator
