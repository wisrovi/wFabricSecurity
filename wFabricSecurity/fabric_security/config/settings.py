"""Settings management for wFabricSecurity."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml

from .defaults import Defaults

logger = logging.getLogger("FabricSecurity.Config")


@dataclass
class Settings:
    """Central configuration for wFabricSecurity."""

    local_data_dir: str = field(default_factory=lambda: Defaults.LOCAL_DATA_DIR)

    fabric_peer_url: str = field(default_factory=lambda: Defaults.FABRIC_PEER_URL)
    fabric_orderer_url: str = field(default_factory=lambda: Defaults.FABRIC_ORDERER_URL)
    fabric_channel: str = field(default_factory=lambda: Defaults.FABRIC_CHANNEL)
    fabric_chaincode: str = field(default_factory=lambda: Defaults.FABRIC_CHAINCODE)
    fabric_tls_ca_file: str = field(default_factory=lambda: Defaults.FABRIC_TLS_CA_FILE)
    fabric_tls_enabled: bool = field(
        default_factory=lambda: Defaults.FABRIC_TLS_ENABLED
    )

    msp_path: str = field(default_factory=lambda: Defaults.MSP_PATH)

    retry_max_attempts: int = field(default_factory=lambda: Defaults.RETRY_MAX_ATTEMPTS)
    retry_backoff_factor: float = field(
        default_factory=lambda: Defaults.RETRY_BACKOFF_FACTOR
    )
    retry_initial_delay: float = field(
        default_factory=lambda: Defaults.RETRY_INITIAL_DELAY
    )

    rate_limit_requests_per_second: int = field(
        default_factory=lambda: Defaults.RATE_LIMIT_REQUESTS_PER_SECOND
    )
    rate_limit_burst: int = field(default_factory=lambda: Defaults.RATE_LIMIT_BURST)

    message_ttl_seconds: int = field(
        default_factory=lambda: Defaults.MESSAGE_TTL_SECONDS
    )
    message_cleanup_interval: int = field(
        default_factory=lambda: Defaults.MESSAGE_CLEANUP_INTERVAL
    )

    cert_cache_size: int = field(default_factory=lambda: Defaults.CERT_CACHE_SIZE)
    cert_cache_ttl_seconds: int = field(
        default_factory=lambda: Defaults.CERT_CACHE_TTL_SECONDS
    )

    log_level: str = field(default_factory=lambda: Defaults.LOG_LEVEL)

    extra_chaincodes: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Settings":
        """Create Settings from environment variables."""
        return cls(
            local_data_dir=os.environ.get(
                "FABRIC_LOCAL_DATA_DIR", Defaults.LOCAL_DATA_DIR
            ),
            fabric_peer_url=os.environ.get("FABRIC_PEER_URL", Defaults.FABRIC_PEER_URL),
            fabric_orderer_url=os.environ.get(
                "FABRIC_ORDERER_URL", Defaults.FABRIC_ORDERER_URL
            ),
            fabric_channel=os.environ.get("FABRIC_CHANNEL", Defaults.FABRIC_CHANNEL),
            fabric_chaincode=os.environ.get(
                "FABRIC_CHAINCODE", Defaults.FABRIC_CHAINCODE
            ),
            fabric_tls_ca_file=os.environ.get(
                "FABRIC_TLS_CA_FILE", Defaults.FABRIC_TLS_CA_FILE
            ),
            fabric_tls_enabled=os.environ.get(
                "FABRIC_TLS_ENABLED", str(Defaults.FABRIC_TLS_ENABLED)
            ).lower()
            == "true",
            msp_path=os.environ.get("FABRIC_MSP_PATH", Defaults.MSP_PATH),
            retry_max_attempts=int(
                os.environ.get("FABRIC_RETRY_MAX_ATTEMPTS", Defaults.RETRY_MAX_ATTEMPTS)
            ),
            retry_backoff_factor=float(
                os.environ.get(
                    "FABRIC_RETRY_BACKOFF_FACTOR", Defaults.RETRY_BACKOFF_FACTOR
                )
            ),
            retry_initial_delay=float(
                os.environ.get(
                    "FABRIC_RETRY_INITIAL_DELAY", Defaults.RETRY_INITIAL_DELAY
                )
            ),
            rate_limit_requests_per_second=int(
                os.environ.get(
                    "FABRIC_RATE_LIMIT_RPS", Defaults.RATE_LIMIT_REQUESTS_PER_SECOND
                )
            ),
            rate_limit_burst=int(
                os.environ.get("FABRIC_RATE_LIMIT_BURST", Defaults.RATE_LIMIT_BURST)
            ),
            message_ttl_seconds=int(
                os.environ.get("FABRIC_MESSAGE_TTL", Defaults.MESSAGE_TTL_SECONDS)
            ),
            message_cleanup_interval=int(
                os.environ.get(
                    "FABRIC_MESSAGE_CLEANUP", Defaults.MESSAGE_CLEANUP_INTERVAL
                )
            ),
            cert_cache_size=int(
                os.environ.get("FABRIC_CERT_CACHE_SIZE", Defaults.CERT_CACHE_SIZE)
            ),
            cert_cache_ttl_seconds=int(
                os.environ.get("FABRIC_CERT_CACHE_TTL", Defaults.CERT_CACHE_TTL_SECONDS)
            ),
            log_level=os.environ.get("FABRIC_LOG_LEVEL", Defaults.LOG_LEVEL),
        )

    @classmethod
    def from_yaml(cls, path: str) -> "Settings":
        """Create Settings from YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            logger.warning(f"Config file not found: {path}, using defaults")
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        return cls(
            local_data_dir=data.get("local_data_dir", Defaults.LOCAL_DATA_DIR),
            fabric_peer_url=data.get("fabric_peer_url", Defaults.FABRIC_PEER_URL),
            fabric_orderer_url=data.get(
                "fabric_orderer_url", Defaults.FABRIC_ORDERER_URL
            ),
            fabric_channel=data.get("fabric_channel", Defaults.FABRIC_CHANNEL),
            fabric_chaincode=data.get("fabric_chaincode", Defaults.FABRIC_CHAINCODE),
            fabric_tls_ca_file=data.get(
                "fabric_tls_ca_file", Defaults.FABRIC_TLS_CA_FILE
            ),
            fabric_tls_enabled=data.get(
                "fabric_tls_enabled", Defaults.FABRIC_TLS_ENABLED
            ),
            msp_path=data.get("msp_path", Defaults.MSP_PATH),
            retry_max_attempts=data.get(
                "retry_max_attempts", Defaults.RETRY_MAX_ATTEMPTS
            ),
            retry_backoff_factor=data.get(
                "retry_backoff_factor", Defaults.RETRY_BACKOFF_FACTOR
            ),
            retry_initial_delay=data.get(
                "retry_initial_delay", Defaults.RETRY_INITIAL_DELAY
            ),
            rate_limit_requests_per_second=data.get(
                "rate_limit_rps", Defaults.RATE_LIMIT_REQUESTS_PER_SECOND
            ),
            rate_limit_burst=data.get("rate_limit_burst", Defaults.RATE_LIMIT_BURST),
            message_ttl_seconds=data.get("message_ttl", Defaults.MESSAGE_TTL_SECONDS),
            message_cleanup_interval=data.get(
                "message_cleanup_interval", Defaults.MESSAGE_CLEANUP_INTERVAL
            ),
            cert_cache_size=data.get("cert_cache_size", Defaults.CERT_CACHE_SIZE),
            cert_cache_ttl_seconds=data.get(
                "cert_cache_ttl", Defaults.CERT_CACHE_TTL_SECONDS
            ),
            log_level=data.get("log_level", Defaults.LOG_LEVEL),
            extra_chaincodes=data.get("extra_chaincodes", []),
        )

    def to_yaml(self, path: str) -> None:
        """Save Settings to YAML file."""
        data = {
            "local_data_dir": self.local_data_dir,
            "fabric_peer_url": self.fabric_peer_url,
            "fabric_orderer_url": self.fabric_orderer_url,
            "fabric_channel": self.fabric_channel,
            "fabric_chaincode": self.fabric_chaincode,
            "fabric_tls_ca_file": self.fabric_tls_ca_file,
            "fabric_tls_enabled": self.fabric_tls_enabled,
            "msp_path": self.msp_path,
            "retry_max_attempts": self.retry_max_attempts,
            "retry_backoff_factor": self.retry_backoff_factor,
            "retry_initial_delay": self.retry_initial_delay,
            "rate_limit_rps": self.rate_limit_requests_per_second,
            "rate_limit_burst": self.rate_limit_burst,
            "message_ttl": self.message_ttl_seconds,
            "message_cleanup_interval": self.message_cleanup_interval,
            "cert_cache_size": self.cert_cache_size,
            "cert_cache_ttl": self.cert_cache_ttl_seconds,
            "log_level": self.log_level,
            "extra_chaincodes": self.extra_chaincodes,
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def configure_settings(settings: Settings) -> None:
    """Configure global settings instance."""
    global _settings
    _settings = settings
