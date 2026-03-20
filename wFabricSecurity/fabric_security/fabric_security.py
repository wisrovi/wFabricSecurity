import hashlib
import functools
import json
import logging
import inspect
import asyncio
from typing import Optional, Dict, Any
from ecdsa import SigningKey, VerifyingKey, NIST256p
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FabricSecurity")


class MockGateway:
    def __init__(self):
        self.private_data: Dict[str, Any] = {}
        self.ledger: Dict[str, str] = {}
        self.keys: Dict[str, str] = {}

    def submit_private_data(self, collection: str, key: str, data: Any):
        self.private_data[key] = data
        logger.info(f"[MockGateway] Private data stored: {key}")

    def get_private_data(self, collection: str, key: str) -> Any:
        return self.private_data.get(key)

    def get_network(self, channel: str):
        return MockNetwork(self)

    def sign(self, data: str) -> str:
        sk = SigningKey.generate(curve=NIST256p)
        vk = sk.get_verifying_key()
        self.keys[data] = vk.to_pem().decode()
        signature = sk.sign(data.encode()).hex()
        logger.info(f"[MockGateway] Data signed")
        return signature

    def verify_signature(self, data: str, signature: str, signer_id: str) -> bool:
        logger.info(f"[MockGateway] Signature verified for {signer_id}")
        return True


class MockNetwork:
    def __init__(self, gateway):
        self.gateway = gateway

    def get_contract(self, name: str):
        return MockContract(self.gateway)


class MockContract:
    def __init__(self, gateway):
        self.gateway = gateway

    def submit_transaction(self, method: str, *args):
        key = args[0] if args else "unknown"
        value = args[1] if len(args) > 1 else ""
        self.gateway.ledger[key] = value
        logger.info(f"[MockContract] Transaction {method}: {key} = {value}")


class FabricSecurity:
    def __init__(
        self,
        me: str,
        peer_url: Optional[str] = None,
        msp_path: Optional[str] = None,
        use_mock: bool = True,
    ):
        self.me = me
        self.peer_url = peer_url or "mock"
        self.msp_path = msp_path or "mock"
        self.use_mock = use_mock

        if use_mock:
            self.gateway = MockGateway()
        else:
            try:
                from fabric_gateway import Gateway

                self.gateway = Gateway(peer_addr=peer_url, msp_path=msp_path)
            except ImportError:
                logger.warning("fabric-gateway not available, using mock mode")
                self.gateway = MockGateway()
                self.use_mock = True

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or inspect.iscoroutinefunction(func)

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
                    if m_id not in trusted_masters or not self.gateway.verify_signature(
                        h_a, m_sig, m_id
                    ):
                        raise PermissionError(f"Master {m_id} no verificado.")

                    result = func(private_payload, *args, **kwargs)
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    contract.submit_transaction("CompleteTask", t_id, h_b)

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
                    if m_id not in trusted_masters or not self.gateway.verify_signature(
                        h_a, m_sig, m_id
                    ):
                        raise PermissionError(f"Master {m_id} no verificado.")

                    result = await func(private_payload, *args, **kwargs)
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    contract.submit_transaction("CompleteTask", t_id, h_b)

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
