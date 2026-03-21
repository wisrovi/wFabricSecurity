"""Fabric Network for wFabricSecurity."""

import logging
from typing import Optional

from .gateway import FabricGateway

logger = logging.getLogger("FabricSecurity.Network")


class FabricNetwork:
    """Represents a Fabric network/channel."""

    def __init__(self, gateway: FabricGateway, channel: str):
        """Initialize Fabric Network.

        Args:
            gateway: Fabric Gateway instance
            channel: Channel name
        """
        self._gateway = gateway
        self._channel = channel

    @property
    def channel(self) -> str:
        """Get channel name."""
        return self._channel

    @property
    def gateway(self) -> FabricGateway:
        """Get gateway."""
        return self._gateway

    def get_contract(self, chaincode: str):
        """Get a contract for a chaincode.

        Args:
            chaincode: Chaincode name

        Returns:
            FabricContract instance
        """
        from .contract import FabricContract

        return FabricContract(self._gateway, self._channel, chaincode)

    def get_default_contract(self):
        """Get the default contract."""
        return self.get_contract(self._gateway.chaincode)
