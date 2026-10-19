"""The finite transition system described in Section 7 of the manuscript.

The manuscript specifies the action vocabulary and the semantic distinctions;
this module fixes one deterministic interpretation of them.  Every
interpretation choice is listed in docs/ASSUMPTIONS.md.  Behaviour is never
read from expected-result files.

Revision 5 semantics (see docs/CHANGELOG_REVISION5.md):
* RequestRevoke is an exogenous policy event and does not require a load.
* After UpdatePolicy the source route is fenced: Read is disabled unless the
  configuration ignores information checks.
* A fenced pending effect is held; it can no longer fire.
* Reports reach operational state only through Release when a release gate
  exists; ReportExport is enabled only in UnguardedExport.
* TimedRelease adds an internal DelayRelease step that is taken only when the
  secret is 1, so release position (not payload) depends on the secret.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .policies import Configuration, policy_for
from .state import State


@dataclass(frozen=True, slots=True)
class Observation:
    kind: str
    payload: object = None


@dataclass(frozen=True, slots=True)
class Transition:
    action: str
    source: State
    target: State
    observation: Observation | None = None


GLOBAL_ACTIONS = (
    "PrepareEffect",
    "RequestRevoke",
    "UpdatePolicy",
    "Isolate",
    "Fence",
    "Persist",
    "CommitCut",
    "OpUse",
    "FireEffect",
    "Review",
    "GenerateReport",
    "Answer",
    "ReportExport",
    "Release",
    "PrivateDeliberation",
    "CleanPublicReconstruct",
    "GrantRevoke",
)

# Internal (non-public) action used only by the TimedRelease variant.  It is
# not part of the public interaction strategy, so the self-composition lets
# one copy take it alone.
INTERNAL_ACTIONS = ("DelayRelease",)


class TransitionSystem:
    """Finite model with explicit action enabling and immutable successors."""

    def __init__(self, configuration: Configuration | str = Configuration.GOVERNED, sources: int = 1,
                 *, secrets: str = "shared", revoked=None, session_cache: bool = True) -> None:
        if sources < 1:
            raise ValueError("the paper model requires at least one restricted source")
        self.configuration = Configuration(configuration)
        self.policy = policy_for(self.configuration)
        self.sources = sources
        if secrets not in {"shared", "independent"}:
            raise ValueError("secrets must be shared or independent")
        self.secrets = secrets
        self.revoked = frozenset(range(sources) if revoked is None else revoked)
        if not self.revoked or not self.revoked <= set(range(sources)):
            raise ValueError("revoked must be a nonempty source subset")
        self.session_cache = session_cache

    def initial(self, secret: int) -> State:
        if not 0 <= secret < (2 if self.secrets == "shared" else 2 ** self.sources):
            raise ValueError("secret valuation is outside the selected finite domain")
        return State.initial(secret, self.sources)

    def bit(self, state: State, index: int) -> int:
        return state.secret if self.secrets == "shared" else (state.secret >> index) & 1

    def has_memory(self, state: State) -> bool:
        return state.has_loaded or any(state.session_cache)

    def restricted(self, state: State) -> bool:
        return state.report_exported or any(state.loaded[i] or state.session_cache[i] for i in self.revoked)

    def release_payload(self, state: State) -> int:
        return state.secret if self.configuration is Configuration.APPROVED_SECRET_RELEASE else 0

    def use_payload(self, state: State) -> int:
        if state.report_exported:
            return state.secret
        if self.has_memory(state):
            if self.secrets == "shared":
                return state.secret
            return sum(self.bit(state, i) << i for i in range(self.sources)
                       if state.loaded[i] or state.session_cache[i])
        return self.release_payload(state) if state.released else 0

    # ------------------------------------------------------------------ guards
    def _source_enabled(self, state: State, index: int, operation: str) -> bool:
        ignore = self.policy.admits_post_cut_source
        if operation == "Read":
            if index in self.revoked and state.policy_updated and not ignore:
                return False  # source route fenced by the policy update
            return not state.read[index]
        if index in self.revoked and state.isolated and not ignore:
            return False  # context isolated: no further derivation or admission
        if operation == "Derive":
            return state.read[index] and not state.derived[index]
        if operation == "Load":
            return state.derived[index] and not state.loaded[index]
        raise AssertionError(operation)

    def _release_ready(self, state: State) -> bool:
        return self.policy.gates_export and state.report_generated and not state.released

    def _global_enabled(self, state: State, action: str) -> bool:
        if action == "PrepareEffect":
            return state.has_loaded and not state.effect_prepared and not state.fenced
        if action == "RequestRevoke":
            return not state.request_revoke and not state.committed
        if action == "UpdatePolicy":
            return state.request_revoke and not state.policy_updated
        if action == "Isolate":
            return state.policy_updated and not state.isolated
        if action == "Fence":
            return state.policy_updated and not state.fenced
        if action == "Persist":
            return state.isolated and state.fenced and not state.evidence_persisted
        if action == "CommitCut":
            return state.isolated and state.fenced and state.evidence_persisted and not state.committed
        if action == "OpUse":
            if self.configuration is Configuration.REFUSAL_MUTATION and self.bit(state, min(self.revoked)) == 1:
                return False
            if not state.committed or state.op_uses >= 1:
                return False
            if state.grant_revoked and self.policy.checks_grant:
                return False
            return self.has_memory(state) or state.report_exported or state.released or state.public_reconstructed
        if action == "FireEffect":
            return state.effect_prepared and not state.effect_fired and not state.fenced
        if action == "Review":
            return state.committed and state.evidence_persisted and not state.review_open
        if action == "GenerateReport":
            return state.review_open and not state.report_generated
        if action == "Answer":
            return state.report_generated and not state.review_answered and not state.evidence_deleted
        if action == "ReportExport":
            return (not self.policy.gates_export) and state.review_answered and not state.report_exported
        if action == "Release":
            if not self._release_ready(state):
                return False
            if self.policy.release_timing_depends_on_secret and self.bit(state, min(self.revoked)) == 1:
                return state.release_delayed
            return True
        if action == "PrivateDeliberation":
            return state.committed and not state.deliberated
        if action == "CleanPublicReconstruct":
            return state.committed and not state.public_reconstructed
        if action == "GrantRevoke":
            return state.committed and not state.grant_revoked
        if action == "DelayRelease":
            return (
                self.policy.release_timing_depends_on_secret
                and self.bit(state, min(self.revoked)) == 1
                and self._release_ready(state)
                and not state.release_delayed
            )
        raise KeyError(action)

    def enabled_actions(self, state: State) -> tuple[str, ...]:
        """Return enabled actions in stable paper order."""

        actions: list[str] = []
        for index in range(self.sources):
            for operation in ("Read", "Derive", "Load"):
                if self._source_enabled(state, index, operation):
                    actions.append(f"{operation}[{index}]")
        actions.extend(action for action in GLOBAL_ACTIONS + INTERNAL_ACTIONS if self._global_enabled(state, action))
        return tuple(actions)

    @staticmethod
    def is_internal(action: str) -> bool:
        return action in INTERNAL_ACTIONS

    # -------------------------------------------------------------- successors
    def _source_successor(self, state: State, index: int, operation: str) -> State:
        field = {"Read": "read", "Derive": "derived", "Load": "loaded"}[operation]
        values = list(getattr(state, field))
        values[index] = True
        changes = {field: tuple(values)}
        if operation == "Load" and self.session_cache:
            cache = list(state.session_cache)
            cache[index] = True
            changes["session_cache"] = tuple(cache)
        return state.replace(**changes)

    def successor(self, state: State, action: str, *, _enabled: bool = False) -> Transition:
        """Apply one enabled action and return its transition."""

        if not _enabled and action not in self.enabled_actions(state):
            raise ValueError(f"action {action!r} is disabled in state {state!r}")
        if "[" in action:
            operation, index_text = action[:-1].split("[")
            target = self._source_successor(state, int(index_text), operation)
            return Transition(action, state, target)

        target = state
        observation: Observation | None = None
        if action == "PrepareEffect":
            target = state.replace(effect_prepared=True)
        elif action == "RequestRevoke":
            target = state.replace(request_revoke=True)
        elif action == "UpdatePolicy":
            target = state.replace(policy_updated=True)
        elif action == "Isolate":
            loaded = state.loaded if self.policy.keeps_loaded_context_at_cut else tuple(v and i not in self.revoked for i,v in enumerate(state.loaded))
            cache = state.session_cache if self.policy.keeps_loaded_context_at_cut else tuple(v and i not in self.revoked for i,v in enumerate(state.session_cache))
            target = state.replace(isolated=True, loaded=loaded, session_cache=cache, evidence_deleted=self.policy.deletes_evidence)
        elif action == "Fence":
            target = state.replace(fenced=True)
        elif action == "Persist":
            target = state.replace(evidence_persisted=True)
        elif action == "CommitCut":
            target = state.replace(committed=True)
        elif action == "OpUse":
            restricted = self.restricted(state)
            bad_authority = state.grant_revoked and not self.policy.checks_grant
            target = state.replace(
                op_uses=state.op_uses + 1,
                unauthorized_info=state.unauthorized_info or restricted,
                unauthorized_authority=state.unauthorized_authority or bad_authority,
            )
            observation = Observation("operational-use", self.use_payload(state))
        elif action == "FireEffect":
            # Pre-fence effects run under the pre-cut grant; the payload is a
            # public tool-call acknowledgement.
            target = state.replace(effect_fired=True)
            observation = Observation("effect", 0)
        elif action == "Review":
            target = state.replace(review_open=True)
        elif action == "GenerateReport":
            target = state.replace(report_generated=True)
        elif action == "Answer":
            target = state.replace(review_answered=True)
        elif action == "ReportExport":
            target = state.replace(report_exported=True)
        elif action == "Release":
            target = state.replace(released=True)
            observation = Observation("release", self.release_payload(state))
        elif action == "PrivateDeliberation":
            target = state.replace(deliberated=True)
        elif action == "CleanPublicReconstruct":
            target = state.replace(public_reconstructed=True, loaded=(False,) * self.sources)
        elif action == "GrantRevoke":
            target = state.replace(grant_revoked=True)
        elif action == "DelayRelease":
            target = state.replace(release_delayed=True)
        else:
            raise KeyError(action)
        return Transition(action, state, target, observation)

    def transitions(self, state: State) -> tuple[Transition, ...]:
        return tuple(self.successor(state, action, _enabled=True) for action in self.enabled_actions(state))

    def is_completion(self, state: State) -> bool:
        return state.committed

    def review_available(self, state: State) -> bool:
        return state.review_answered

    def info_safe(self, state: State) -> bool:
        return not state.unauthorized_info

    def auth_safe(self, state: State) -> bool:
        return not state.unauthorized_authority


def all_configurations() -> tuple[Configuration, ...]:
    return tuple(Configuration)


def all_transitions(system: TransitionSystem, state: State) -> Iterable[Transition]:
    return system.transitions(state)
