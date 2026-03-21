"""Communication permissions for wFabricSecurity."""

import logging
from typing import List, Optional, Set

from ..core.enums import CommunicationDirection, ParticipantStatus
from ..core.exceptions import PermissionDeniedError, RevocationError
from ..core.models import Participant

logger = logging.getLogger("FabricSecurity.Permissions")


class PermissionManager:
    """Manages communication permissions between participants."""

    def __init__(self, gateway: "FabricGateway"):
        """Initialize permission manager.

        Args:
            gateway: Fabric Gateway instance
        """
        self._gateway = gateway
        self._revoked_cache: Set[str] = set()

    def register_communication(
        self,
        from_identity: str,
        to_identity: str,
        direction: CommunicationDirection = CommunicationDirection.BIDIRECTIONAL,
    ) -> dict:
        """Register a communication permission.

        Args:
            from_identity: Source participant identity
            to_identity: Target participant identity
            direction: Communication direction

        Returns:
            Registration result
        """
        participant_data = self._get_participant_data(from_identity)

        if not participant_data:
            participant_data = {
                "identity": from_identity,
                "code_hash": "",
                "version": "1.0.0",
                "registered_at": "",
                "allowed_communications": [],
                "direction": direction.value,
                "is_active": True,
            }

        if to_identity not in participant_data["allowed_communications"]:
            participant_data["allowed_communications"].append(to_identity)

        participant_data["direction"] = direction.value

        if self._gateway.is_using_fabric:
            result = self._gateway.fabric_storage.register_participant(participant_data)
            if result.get("status") == "success":
                return result

        self._gateway.local_storage.save(
            f"participant_{from_identity}", participant_data
        )
        return {"status": "success", "tx_id": "local"}

    def can_communicate_with(
        self,
        from_identity: str,
        to_identity: str,
    ) -> bool:
        """Check if communication is allowed.

        Args:
            from_identity: Source participant identity
            to_identity: Target participant identity

        Returns:
            True if communication is allowed

        Raises:
            PermissionDeniedError: If communication is denied
            RevocationError: If participant is revoked
        """
        if self.is_revoked(from_identity):
            raise RevocationError(
                message=f"Participant {from_identity} has been revoked.",
                details={"participant_id": from_identity},
            )

        if self.is_revoked(to_identity):
            raise RevocationError(
                message=f"Participant {to_identity} has been revoked.",
                details={"participant_id": to_identity},
            )

        from_participant = self._get_participant_data(from_identity)
        if not from_participant:
            logger.warning(
                f"No participant data for {from_identity}, allowing communication"
            )
            return True

        if not from_participant.get("is_active", True):
            raise PermissionDeniedError(
                message=f"Participant {from_identity} is not active.",
                details={"participant_id": from_identity},
            )

        direction = CommunicationDirection(
            from_participant.get("direction", "bidirectional")
        )
        allowed = from_participant.get("allowed_communications", [])

        if direction == CommunicationDirection.BIDIRECTIONAL:
            return True

        if direction == CommunicationDirection.OUTBOUND:
            if to_identity not in allowed:
                raise PermissionDeniedError(
                    message=f"{from_identity} is not allowed to communicate with {to_identity}.",
                    details={
                        "from": from_identity,
                        "to": to_identity,
                        "allowed": allowed,
                    },
                )
            return True

        return True

    def revoke_participant(self, participant_id: str) -> dict:
        """Revoke a participant.

        Args:
            participant_id: Participant to revoke

        Returns:
            Revocation result
        """
        self._revoked_cache.add(participant_id)

        if self._gateway.is_using_fabric:
            participant = self._gateway.fabric_storage.get_participant(participant_id)
            if participant:
                participant["is_active"] = False
                participant["status"] = ParticipantStatus.REVOKED.value
                return self._gateway.fabric_storage.register_participant(participant)

        participant_data = self._gateway.local_storage.get(
            f"participant_{participant_id}"
        )
        if not participant_data:
            participant_data = {
                "identity": participant_id,
                "code_hash": "",
                "version": "1.0.0",
                "is_active": False,
                "status": ParticipantStatus.REVOKED.value,
            }
        else:
            participant_data["is_active"] = False
            participant_data["status"] = ParticipantStatus.REVOKED.value

        self._gateway.local_storage.add_revoked_participant(participant_id)
        self._gateway.local_storage.save(
            f"participant_{participant_id}", participant_data
        )

        return {"status": "success", "tx_id": "local", "revoked": participant_id}

    def is_revoked(self, participant_id: str) -> bool:
        """Check if a participant is revoked.

        Args:
            participant_id: Participant to check

        Returns:
            True if revoked
        """
        if participant_id in self._revoked_cache:
            return True

        if self._gateway.local_storage.is_participant_revoked(participant_id):
            self._revoked_cache.add(participant_id)
            return True

        return False

    def get_revoked_participants(self) -> List[str]:
        """Get list of all revoked participants.

        Returns:
            List of revoked participant IDs
        """
        revoked = set(self._revoked_cache)
        revoked.update(self._gateway.local_storage.get_revoked_participants())
        return sorted(revoked)

    def get_allowed_communications(self, participant_id: str) -> List[str]:
        """Get list of allowed communication targets.

        Args:
            participant_id: Participant identity

        Returns:
            List of allowed target identities
        """
        participant = self._get_participant_data(participant_id)
        if participant:
            return participant.get("allowed_communications", [])
        return []

    def _get_participant_data(self, identity: str) -> Optional[dict]:
        """Get participant data from Fabric or local storage.

        Args:
            identity: Participant identity

        Returns:
            Participant data or None
        """
        if self._gateway.is_using_fabric:
            participant = self._gateway.fabric_storage.get_participant(identity)
            if participant:
                return participant

        return self._gateway.local_storage.get(f"participant_{identity}")

    def update_participant(
        self,
        identity: str,
        updates: dict,
    ) -> dict:
        """Update participant data.

        Args:
            identity: Participant identity
            updates: Fields to update

        Returns:
            Update result
        """
        participant = self._get_participant_data(identity)

        if not participant:
            participant = {
                "identity": identity,
                "code_hash": "",
                "version": "1.0.0",
                "is_active": True,
            }

        participant.update(updates)

        if self._gateway.is_using_fabric:
            return self._gateway.fabric_storage.register_participant(participant)

        self._gateway.local_storage.save(f"participant_{identity}", participant)
        return {"status": "success", "tx_id": "local"}
