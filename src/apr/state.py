"""Immutable transition-system state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class State:
    """Finite state vector used by both the explorer and result serializers."""

    secret: int
    read: tuple[bool, ...]
    derived: tuple[bool, ...]
    loaded: tuple[bool, ...]
    request_revoke: bool = False
    policy_updated: bool = False
    isolated: bool = False
    fenced: bool = False
    evidence_persisted: bool = False
    committed: bool = False
    effect_prepared: bool = False
    effect_fired: bool = False
    grant_revoked: bool = False
    review_open: bool = False
    report_generated: bool = False
    review_answered: bool = False
    report_exported: bool = False
    released: bool = False
    deliberated: bool = False
    clean_rebuilt: bool = False
    public_reconstructed: bool = False
    evidence_deleted: bool = False
    op_uses: int = 0
    unauthorized_info: bool = False
    unauthorized_authority: bool = False

    @classmethod
    def initial(cls, secret: int, sources: int) -> "State":
        return cls(secret=secret, read=(False,) * sources, derived=(False,) * sources, loaded=(False,) * sources)

    @property
    def has_loaded(self) -> bool:
        return any(self.loaded)

    @property
    def has_derived(self) -> bool:
        return any(self.derived)

    @property
    def loaded_mask(self) -> int:
        return sum((1 << i) for i, value in enumerate(self.loaded) if value)

    @property
    def restricted_payload(self) -> int:
        """The finite paper model uses one bit per source as the secret payload."""

        return self.secret

    def replace(self, **changes: object) -> "State":
        """Return a new state with selected fields changed."""

        values = {field: getattr(self, field) for field in self.__dataclass_fields__}
        values.update(changes)
        return type(self)(**values)
