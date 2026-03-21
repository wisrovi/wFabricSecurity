"""Default configuration values for wFabricSecurity."""

from dataclasses import dataclass


@dataclass
class Defaults:
    """Default values for wFabricSecurity configuration."""

    LOCAL_DATA_DIR: str = "/tmp/fabric_security_data"

    FABRIC_PEER_URL: str = "localhost:7051"
    FABRIC_ORDERER_URL: str = "orderer.net:7050"
    FABRIC_CHANNEL: str = "mychannel"
    FABRIC_CHAINCODE: str = "tasks"
    FABRIC_TLS_CA_FILE: str = "/etc/hyperledger/fabric/msp/tlscacerts/tlsroot.pem"
    FABRIC_TLS_ENABLED: bool = False

    MSP_PATH: str = (
        "enviroment/organizations/peerOrganizations/org1.net/users/Admin@org1.net/msp"
    )

    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 1.5
    RETRY_INITIAL_DELAY: float = 0.5

    RATE_LIMIT_REQUESTS_PER_SECOND: int = 100
    RATE_LIMIT_BURST: int = 200

    MESSAGE_TTL_SECONDS: int = 3600
    MESSAGE_CLEANUP_INTERVAL: int = 300

    CERT_CACHE_SIZE: int = 100
    CERT_CACHE_TTL_SECONDS: int = 3600

    LOG_LEVEL: str = "INFO"
