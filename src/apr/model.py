"""The independent finite transition system described by Section 7.

The manuscript specifies the action vocabulary and the semantic distinctions but
does not publish the original state vector or guards. This module is a small,
deterministic interpretation of those definitions. Its behavior is never read
from expected-result files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .policies import Configuration, Policy, policy_for
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


class TransitionSystem:
    """Finite model with explicit action enabling and immutable successors."""

    def __init__(self, configuration: Configuration | str = Configuration.GOVERNED, sources: int = 1) -> None:
        if sources < 1:
            raise ValueError("the paper model requires at least one restricted source")
        self.configuration = Configuration(configuration)
        self.policy = policy_for(self.configuration)
        self.sources = sources

    def initial(self, secret: int) -> State:
        if secret not in (0, 1):
            raise ValueError("the finite paper model uses one-bit secrets 0 and 1")
        return State.initial(secret, self.sources)

    def _source_enabled(self, state: State, index: int, operation: str) -> bool:
        if state.isolated and not self.policy.admits_post_cut_source:
            return False
        if operation == "Read":
            return not state.read[index]
        if operation == "Derive":
            return state.read[index] and not state.derived[index]
        if operation == "Load":
            return state.derived[index] and not state.loaded[index]
        raise AssertionError(operation)

    def _global_enabled(self, state: State, action: str) -> bool:
        if action == "PrepareEffect":
            return state.has_loaded and not state.effect_prepared and not state.committed
        if action == "RequestRevoke":
            return state.has_loaded and not state.request_revoke and not state.committed
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
            if not state.committed or state.op_uses >= 1:
                return False
            if state.grant_revoked and self.policy.checks_grant:
                return False
            return state.has_loaded or state.report_exported or state.released or state.public_reconstructed
        if action == "FireEffect":
            return state.fenced and state.effect_prepared and not state.effect_fired
        if action == "Review":
            return state.committed and state.evidence_persisted and not state.review_open
        if action == "GenerateReport":
            return state.review_open and not state.report_generated
        if action == "Answer":
            return state.report_generated and not state.review_answered and not state.evidence_deleted
        if action == "ReportExport":
            return state.review_answered and not state.report_exported
        if action == "Release":
            if not (state.report_generated or state.report_exported) or state.released or not self.policy.gates_export:
                return False
            return True
        if action == "PrivateDeliberation":
            return state.committed and not state.deliberated
        if action == "CleanPublicReconstruct":
            return state.committed and not state.public_reconstructed
        if action == "GrantRevoke":
            return state.committed and not state.grant_revoked
        raise KeyError(action)

    def enabled_actions(self, state: State) -> tuple[str, ...]:
        """Return enabled actions in stable paper order."""

        actions: list[str] = []
        for index in range(self.sources):
            for operation in ("Read", "Derive", "Load"):
                if self._source_enabled(state, index, operation):
                    actions.append(f"{operation}[{index}]")
        actions.extend(action for action in GLOBAL_ACTIONS if self._global_enabled(state, action))
        return tuple(actions)

    def _source_successor(self, state: State, index: int, operation: str) -> State:
        field = {"Read": "read", "Derive": "derived", "Load": "loaded"}[operation]
        values = list(getattr(state, field))
        values[index] = True
        return state.replace(**{field: tuple(values)})

    def successor(self, state: State, action: str) -> Transition:
        """Apply one enabled action and return its transition."""

        if action not in self.enabled_actions(state):
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
            loaded = state.loaded if self.policy.keeps_loaded_context_at_cut else (False,) * self.sources
            deleted = self.policy.deletes_evidence
            target = state.replace(isolated=True, loaded=loaded, evidence_deleted=deleted)
        elif action == "Fence":
            target = state.replace(fenced=True)
        elif action == "Persist":
            target = state.replace(evidence_persisted=True)
        elif action == "CommitCut":
            target = state.replace(committed=True)
        elif action == "OpUse":
            restricted = state.has_loaded or (
                self.configuration is Configuration.UNGUARDED_EXPORT and state.report_exported
            )
            bad_authority = state.grant_revoked and not self.policy.checks_grant
            target = state.replace(
                op_uses=state.op_uses + 1,
                unauthorized_info=state.unauthorized_info or restricted,
                unauthorized_authority=state.unauthorized_authority or bad_authority,
            )
            if restricted:
                observation = Observation("operational-use", state.restricted_payload)
            else:
                observation = Observation("operational-use", 0)
        elif action == "FireEffect":
            target = state.replace(effect_fired=True)
            if state.grant_revoked and not self.policy.checks_grant:
                target = target.replace(unauthorized_authority=True)
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
            observation = Observation("release", 0)
        elif action == "PrivateDeliberation":
            target = state.replace(deliberated=True)
        elif action == "CleanPublicReconstruct":
            target = state.replace(public_reconstructed=True, loaded=(False,) * self.sources)
        elif action == "GrantRevoke":
            target = state.replace(grant_revoked=True)
        else:
            raise KeyError(action)
        return Transition(action, state, target, observation)

    def transitions(self, state: State) -> tuple[Transition, ...]:
        return tuple(self.successor(state, action) for action in self.enabled_actions(state))

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
