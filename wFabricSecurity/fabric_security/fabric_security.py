import os
import json
import hashlib
import functools
import asyncio
import logging
import subprocess
import tempfile
import base64
import hashlib
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FabricSecurity")

LOCAL_DATA_DIR = Path(tempfile.gettempdir()) / "fabric_security_data"
LOCAL_DATA_DIR.mkdir(exist_ok=True)


class CodeIntegrityError(Exception):
    """Excepción cuando el código ha sido modificado."""

    pass


class FabricGateway:
    def __init__(self, peer_url: str, msp_path: str):
        self.peer_url = peer_url
        self.msp_path = msp_path
        self.channel = "mychannel"
        self.chaincode = "tasks"
        self._use_fabric = False
        self._private_key = None
        self._certificate = None
        self._load_identity()
        self._check_fabric()

    def _load_identity(self):
        """Carga la clave privada y certificado desde el MSP."""
        keystore_dir = Path(self.msp_path) / "keystore"
        signcerts_dir = Path(self.msp_path) / "signcerts"

        try:
            key_files = list(keystore_dir.glob("*"))
            if key_files:
                with open(key_files[0], "rb") as f:
                    self._private_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
                logger.info(f"[FabricGateway] Clave privada: {key_files[0].name}")

            cert_files = list(signcerts_dir.glob("*.pem"))
            if cert_files:
                with open(cert_files[0], "rb") as f:
                    self._certificate = load_pem_x509_certificate(
                        f.read(), backend=default_backend()
                    )
                logger.info(f"[FabricGateway] Certificado: {cert_files[0].name}")
        except Exception as e:
            logger.warning(f"[FabricGateway] No se pudo cargar identidad: {e}")

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

    def compute_code_hash(self, code_paths: list) -> str:
        """
        Calcula el hash SHA-256 de uno o más archivos de código.
        Incluye contenido + nombre de archivo para detectar renombrado.
        """
        hasher = hashlib.sha256()

        for code_path in sorted(code_paths):
            path = Path(code_path)
            if path.is_file():
                hasher.update(f"FILE:{path.name}".encode())
                with open(path, "rb") as f:
                    hasher.update(f.read())
            elif path.is_dir():
                for file_path in sorted(path.rglob("*.py")):
                    hasher.update(f"FILE:{file_path.relative_to(path)}".encode())
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())

        return f"sha256:{hasher.hexdigest()}"

    def sign(self, data: str, signer_id: str = "") -> str:
        """Firma usando ECDSA con la clave privada del MSP."""
        if self._private_key is None:
            import hmac

            key = (data + signer_id).encode()
            logger.warning("[FabricGateway] Sin clave privada, usando HMAC")
            return hmac.new(key, key, hashlib.sha256).hexdigest()

        try:
            data_bytes = data.encode()

            signature = self._private_key.sign(data_bytes, ec.ECDSA(hashes.SHA256()))

            signature_b64 = base64.b64encode(signature).decode()
            logger.info(f"[FabricGateway] Firma ECDSA creada")
            return signature_b64
        except Exception as e:
            logger.error(f"[FabricGateway] Error firmando: {e}")
            raise e

    def verify_signature(self, data: str, signature_b64: str, signer_id: str) -> bool:
        """Verifica firma ECDSA usando el certificado del signer."""
        try:
            cert_pem = self._get_signer_certificate(signer_id)
            if cert_pem is None:
                logger.warning(
                    f"[FabricGateway] No se encontró certificado para {signer_id}"
                )
                return True

            certificate = load_pem_x509_certificate(
                cert_pem.encode(), default_backend()
            )
            public_key = certificate.public_key()

            signature = base64.b64decode(signature_b64)
            data_bytes = data.encode()

            public_key.verify(signature, data_bytes, ec.ECDSA(hashes.SHA256()))
            logger.info(f"[FabricGateway] Firma verificada para {signer_id}")
            return True
        except Exception as e:
            logger.warning(f"[FabricGateway] Verificación fallida: {e}")
            return False

    def _get_signer_certificate(self, signer_id: str) -> Optional[str]:
        """Obtiene el certificado PEM de un signer."""
        if self._use_fabric:
            success, output = self._run_cli(
                [
                    "chaincode",
                    "query",
                    "-C",
                    self.channel,
                    "-n",
                    self.chaincode,
                    "-c",
                    json.dumps({"Args": ["GetCertificate", signer_id]}),
                ]
            )
            if success and "Error:" not in output:
                return output.strip()

        cert_data = self._local_get(f"cert_{signer_id}")
        if cert_data:
            return cert_data.get("cert_pem")
        return None

    def get_certificate_pem(self) -> Optional[str]:
        """Retorna el certificado PEM de esta identidad."""
        if self._certificate:
            return self._certificate.public_bytes(serialization.Encoding.PEM).decode()
        return None

    def get_signer_id(self) -> str:
        """Retorna el CN (Common Name) del certificado como identificador."""
        if self._certificate:
            return self._certificate.subject.rfc4514_string()
        return "Unknown"

    def get_signer_cn(self) -> str:
        """Retorna solo el CN (Common Name) del certificado."""
        if self._certificate:
            for attr in self._certificate.subject:
                if attr.oid == (2, 5, 4, 3):
                    return attr.value
        return "Unknown"

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

    def register_certificate(self):
        """Registra el certificado de esta identidad en Fabric."""
        signer_id = self.get_signer_id()
        cert_pem = self.get_certificate_pem()
        if cert_pem:
            result = self.invoke_chaincode("RegisterCertificate", signer_id, cert_pem)
            self._local_save(f"cert_{signer_id}", {"cert_pem": cert_pem})
            return result
        return None

    def register_code_identity(self, code_paths: list, version: str = "1.0.0"):
        """
        Registra la identidad de código en Fabric.

        Args:
            code_paths: Lista de archivos/directorios a incluir en el hash
            version: Versión del código (e.g., "1.0.0")

        Returns:
            Dict con identity, code_hash, version y timestamp
        """
        signer_id = self.get_signer_id()
        code_hash = self.compute_code_hash(code_paths)
        timestamp = datetime.utcnow().isoformat() + "Z"

        identity_data = {
            "identity": signer_id,
            "cn": self.get_signer_cn(),
            "code_hash": code_hash,
            "version": version,
            "timestamp": timestamp,
            "cert_pem": self.get_certificate_pem(),
        }

        result = self.invoke_chaincode(
            "RegisterCodeIdentity", signer_id, code_hash, version, timestamp
        )

        self._local_save(f"code_id_{signer_id}", identity_data)
        logger.info(
            f"[FabricGateway] Código registrado: {code_hash[:20]}... v{version}"
        )

        return identity_data

    def verify_code_integrity(self, code_paths: list, signer_id: str = None) -> bool:
        """
        Verifica que el código no ha sido modificado desde el último registro.

        Args:
            code_paths: Archivos/directorios a verificar
            signer_id: Si se especifica, verifica solo ese signer. Si no, usa el propio.

        Returns:
            True si el código es íntegro, False si fue modificado

        Raises:
            CodeIntegrityError: Si el código fue modificado
        """
        if signer_id is None:
            signer_id = self.get_signer_id()

        current_hash = self.compute_code_hash(code_paths)

        if self._use_fabric:
            success, output = self._run_cli(
                [
                    "chaincode",
                    "query",
                    "-C",
                    self.channel,
                    "-n",
                    self.chaincode,
                    "-c",
                    json.dumps({"Args": ["GetCodeHash", signer_id]}),
                ]
            )
            if success and "Error:" not in output:
                registered_hash = output.strip()
            else:
                registered_data = self._local_get(f"code_id_{signer_id}")
                registered_hash = (
                    registered_data.get("code_hash") if registered_data else None
                )
        else:
            registered_data = self._local_get(f"code_id_{signer_id}")
            registered_hash = (
                registered_data.get("code_hash") if registered_data else None
            )

        if registered_hash is None:
            logger.warning(f"[FabricGateway] Código no registrado para {signer_id}")
            return True

        if current_hash != registered_hash:
            logger.error(f"[FabricGateway] ALERTA: Código modificado!")
            logger.error(f"[FabricGateway]   Hash actual: {current_hash[:20]}...")
            logger.error(
                f"[FabricGateway]   Hash registrado: {registered_hash[:20]}..."
            )
            raise CodeIntegrityError(
                f"El código de {signer_id} ha sido modificado. "
                f"Hash actual: {current_hash}, Hash registrado: {registered_hash}"
            )

        logger.info(f"[FabricGateway] Código íntegro para {signer_id}")
        return True

    def get_code_history(self, signer_id: str = None) -> list:
        """Obtiene el historial de versiones de código registradas en Fabric."""
        if signer_id is None:
            signer_id = self.get_signer_id()

        if self._use_fabric:
            success, output = self._run_cli(
                [
                    "chaincode",
                    "query",
                    "-C",
                    self.channel,
                    "-n",
                    self.chaincode,
                    "-c",
                    json.dumps({"Args": ["GetCodeHistory", signer_id]}),
                ]
            )
            if success and "Error:" not in output:
                try:
                    return json.loads(output)
                except:
                    pass

        return []


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
        default_msp_path = os.environ.get("FABRIC_MSP_PATH") or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "enviroment",
            "organizations",
            "peerOrganizations",
            "org1.net",
            "users",
            me if "@" in me else f"{me}@org1.net",
            "msp",
        )

        if not os.path.exists(msp_path or default_msp_path):
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
            peer_url=peer_url or os.environ.get("FABRIC_PEER_URL", "localhost:7051"),
            msp_path=msp_path or default_msp_path,
        )

    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or (
            hasattr(func, "__code__") and func.__code__.co_flags & 0x80
        )

    def register_identity(self):
        """Registra el certificado de esta identidad en Fabric."""
        return self.gateway.register_certificate()

    def register_code(self, code_paths: list, version: str = "1.0.0"):
        """
        Registra el hash del código en Fabric.

        Args:
            code_paths: Lista de archivos/directorios a incluir
            version: Versión semver del código

        Usage:
            # Registrar al iniciar
            security = FabricSecurity("Master")
            security.register_code(["master.py", "utils.py"], "1.0.0")
        """
        return self.gateway.register_code_identity(code_paths, version)

    def verify_code(self, code_paths: list = None, signer_id: str = None) -> bool:
        """
        Verifica la integridad del código.

        Args:
            code_paths: Archivos a verificar. Si None, usa __file__ del llamador
            signer_id: ID del signer a verificar

        Usage:
            # Verificar antes de ejecutar operación sensible
            security.verify_code(["master.py"])

        Raises:
            CodeIntegrityError: Si el código fue modificado
        """
        if code_paths is None:
            import traceback

            caller_frame = traceback.extract_stack()[-2]
            code_paths = [caller_frame.filename]

        return self.gateway.verify_code_integrity(code_paths, signer_id)

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
                signer_id = self.gateway.get_signer_id()

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
                    my_sig = self.gateway.sign(hash_a, signer_id)

                    response = func(
                        payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise ConnectionRefusedError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
                    raise e

            @functools.wraps(func)
            async def wrapper_async(payload, *args, **kwargs):
                hash_a = hashlib.sha256(
                    json.dumps(payload, sort_keys=True).encode()
                ).hexdigest()
                task_id = f"{task_prefix}_{hash_a[:12]}"
                signer_id = self.gateway.get_signer_id()

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
                    my_sig = self.gateway.sign(hash_a, signer_id)

                    response = await func(
                        payload, task_id, hash_a, my_sig, signer_id, *args, **kwargs
                    )

                    if response and response.get("slave_id") not in trusted_slaves:
                        logger.warning(
                            f"[Master {signer_id}] Slave no autorizado: {response.get('slave_id')}"
                        )
                    if response and not self.gateway.verify_signature(
                        response.get("hash_b", ""),
                        response.get("slave_sig", ""),
                        response.get("slave_id", ""),
                    ):
                        raise ConnectionRefusedError("Firma del Slave inválida.")

                    logger.info(f"[Master {signer_id}] Task {task_id} completado")
                    return response
                except Exception as e:
                    logger.error(f"Error Master {signer_id}: {e}")
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
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} no verificado, continuando..."
                        )

                    result = func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    signer_id = self.gateway.get_signer_id()

                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction("CompleteTask", t_id, h_b)
                    logger.info(f"[FabricGateway] CompleteTask: {cc_result}")

                    logger.info(f"[Slave {signer_id}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, signer_id),
                        "slave_id": signer_id,
                    }
                except Exception as e:
                    logger.error(f"Error Slave: {e}")
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
                            f"[Slave {self.gateway.get_signer_id()}] Master {m_id} no verificado, continuando..."
                        )

                    result = await func(
                        private_payload or request_data.get("payload", {}),
                        *args,
                        **kwargs,
                    )
                    h_b = hashlib.sha256(
                        json.dumps(result, sort_keys=True).encode()
                    ).hexdigest()
                    signer_id = self.gateway.get_signer_id()

                    contract = self.gateway.get_network("mychannel").get_contract(
                        "tasks"
                    )
                    cc_result = contract.submit_transaction("CompleteTask", t_id, h_b)
                    logger.info(f"[FabricGateway] CompleteTask: {cc_result}")

                    logger.info(f"[Slave {signer_id}] Task {t_id} completado")
                    return {
                        "result": result,
                        "hash_b": h_b,
                        "slave_sig": self.gateway.sign(h_b, signer_id),
                        "slave_id": signer_id,
                    }
                except Exception as e:
                    logger.error(f"Error Slave: {e}")
                    raise e

            return wrapper_async if is_async else wrapper_sync

        return decorator
