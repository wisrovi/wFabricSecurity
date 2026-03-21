"""Decorators for Zero Trust security in wFabricSecurity."""

import functools
import asyncio
import logging
import hashlib
import json
import traceback
from typing import Callable, List, Optional

from ..core.exceptions import CodeIntegrityError, SignatureError, PermissionDeniedError
from .integrity import IntegrityVerifier

logger = logging.getLogger("FabricSecurity.Decorators")


def master_audit(
    task_prefix: str,
    trusted_slaves: Optional[List[str]] = None,
    collection: str = "assetCollection",
    verify_code: bool = True,
):
    """Decorator for master (sender) role in Zero Trust pattern.

    Registers task in Fabric and verifies slave response signature.

    Args:
        task_prefix: Prefix for task ID
        trusted_slaves: List of allowed slave identities
        collection: Private data collection name
        verify_code: Whether to verify own code before execution

    Returns:
        Decorated function
    """
    trusted_slaves = trusted_slaves or []

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

        @functools.wraps(func)
        def wrapper_sync(
            payload: dict,
            task_id: Optional[str] = None,
            hash_a: Optional[str] = None,
            sig: Optional[str] = None,
            my_id: Optional[str] = None,
            *args,
            **kwargs,
        ):
            gateway = kwargs.get("gateway") or getattr(func, "_gateway", None)
            if not gateway:
                raise ValueError("gateway not provided in kwargs or decorator")

            if verify_code:
                verifier = IntegrityVerifier(gateway)
                verifier.verify_own_code()

            if hash_a is None:
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()

            if task_id is None:
                task_id = f"{task_prefix}_{hash_a[:12]}"

            signer_id = my_id or gateway.get_signer_id()

            gateway.invoke_chaincode("RegisterTask", task_id, hash_a)
            my_sig = gateway.sign(hash_a, signer_id)

            try:
                response = func(
                    payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                )

                if response:
                    slave_id = response.get("slave_id")
                    if slave_id and trusted_slaves and slave_id not in trusted_slaves:
                        logger.warning(f"[Master] Untrusted slave: {slave_id}")

                    if not gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        slave_id or "",
                    ):
                        raise SignatureError("Invalid slave signature")

                logger.info(f"[Master {signer_id}] Task {task_id} completed")
                return response
            except Exception as e:
                logger.error(f"[Master] Error: {e}")
                raise

        @functools.wraps(func)
        async def wrapper_async(
            payload: dict,
            task_id: Optional[str] = None,
            hash_a: Optional[str] = None,
            sig: Optional[str] = None,
            my_id: Optional[str] = None,
            *args,
            **kwargs,
        ):
            gateway = kwargs.get("gateway") or getattr(func, "_gateway", None)
            if not gateway:
                raise ValueError("gateway not provided in kwargs or decorator")

            if verify_code:
                verifier = IntegrityVerifier(gateway)
                verifier.verify_own_code()

            if hash_a is None:
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()

            if task_id is None:
                task_id = f"{task_prefix}_{hash_a[:12]}"

            signer_id = my_id or gateway.get_signer_id()

            gateway.invoke_chaincode("RegisterTask", task_id, hash_a)
            my_sig = gateway.sign(hash_a, signer_id)

            try:
                response = await func(
                    payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                )

                if response:
                    slave_id = response.get("slave_id")
                    if slave_id and trusted_slaves and slave_id not in trusted_slaves:
                        logger.warning(f"[Master] Untrusted slave: {slave_id}")

                    if not gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        slave_id or "",
                    ):
                        raise SignatureError("Invalid slave signature")

                logger.info(f"[Master {signer_id}] Task {task_id} completed")
                return response
            except Exception as e:
                logger.error(f"[Master] Error: {e}")
                raise

        return wrapper_async if is_async else wrapper_sync

    return decorator


def slave_verify(
    trusted_masters: Optional[List[str]] = None,
    collection: str = "assetCollection",
    verify_code: bool = True,
):
    """Decorator for slave (receiver) role in Zero Trust pattern.

    Verifies master request and signs response.

    Args:
        trusted_masters: List of allowed master identities
        collection: Private data collection name
        verify_code: Whether to verify own code before execution

    Returns:
        Decorated function
    """
    trusted_masters = trusted_masters or []

    def decorator(func: Callable) -> Callable:
        is_async = asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

        @functools.wraps(func)
        def wrapper_sync(request_data: dict, *args, **kwargs):
            gateway = kwargs.get("gateway") or getattr(func, "_gateway", None)
            if not gateway:
                raise ValueError("gateway not provided in kwargs or decorator")

            if verify_code:
                verifier = IntegrityVerifier(gateway)
                verifier.verify_own_code()

            t_id = request_data.get("task_id")
            h_a = request_data.get("hash_a")
            m_sig = request_data.get("signature")
            m_id = request_data.get("signer_id")

            if not all([t_id, h_a, m_sig, m_id]):
                raise ValueError("Missing required request fields")

            private_payload = gateway.get_private_data(collection, t_id)

            if trusted_masters and m_id not in trusted_masters:
                logger.warning(f"[Slave] Untrusted master: {m_id}")

            try:
                result = func(
                    private_payload or request_data.get("payload", {}),
                    *args,
                    **kwargs,
                )

                h_b = hashlib.sha256(
                    json.dumps(result, sort_keys=True).encode()
                ).hexdigest()

                signer_id = gateway.get_signer_id()
                gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                logger.info(f"[Slave {signer_id}] Task {t_id} completed")
                return {
                    "result": result,
                    "hash_b": h_b,
                    "slave_sig": gateway.sign(h_b, signer_id),
                    "slave_id": signer_id,
                }
            except Exception as e:
                logger.error(f"[Slave] Error: {e}")
                raise

        @functools.wraps(func)
        async def wrapper_async(request_data: dict, *args, **kwargs):
            gateway = kwargs.get("gateway") or getattr(func, "_gateway", None)
            if not gateway:
                raise ValueError("gateway not provided in kwargs or decorator")

            if verify_code:
                verifier = IntegrityVerifier(gateway)
                verifier.verify_own_code()

            t_id = request_data.get("task_id")
            h_a = request_data.get("hash_a")
            m_sig = request_data.get("signature")
            m_id = request_data.get("signer_id")

            if not all([t_id, h_a, m_sig, m_id]):
                raise ValueError("Missing required request fields")

            private_payload = gateway.get_private_data(collection, t_id)

            if trusted_masters and m_id not in trusted_masters:
                logger.warning(f"[Slave] Untrusted master: {m_id}")

            try:
                result = await func(
                    private_payload or request_data.get("payload", {}),
                    *args,
                    **kwargs,
                )

                h_b = hashlib.sha256(
                    json.dumps(result, sort_keys=True).encode()
                ).hexdigest()

                signer_id = gateway.get_signer_id()
                gateway.invoke_chaincode("CompleteTask", t_id, h_b)

                logger.info(f"[Slave {signer_id}] Task {t_id} completed")
                return {
                    "result": result,
                    "hash_b": h_b,
                    "slave_sig": gateway.sign(h_b, signer_id),
                    "slave_id": signer_id,
                }
            except Exception as e:
                logger.error(f"[Slave] Error: {e}")
                raise

        return wrapper_async if is_async else wrapper_sync

    return decorator
