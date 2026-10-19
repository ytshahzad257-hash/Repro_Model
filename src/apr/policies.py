"""Named manuscript configurations and their semantic switches."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Configuration(str, Enum):
    GOVERNED = "Governed"
    SOURCE_ONLY = "SourceOnly"
    IGNORE_INFO_CHECKS = "IgnoreInfoChecks"
    UNGUARDED_EXPORT = "UnguardedExport"
    DELETE_EVIDENCE = "DeleteEvidence"
    IGNORE_GRANT_CHECKS = "IgnoreGrantChecks"
    TIMED_RELEASE = "TimedRelease"
    APPROVED_SECRET_RELEASE = "ApprovedSecretRelease"
    REFUSAL_MUTATION = "RefusalMutation"


@dataclass(frozen=True, slots=True)
class Policy:
    configuration: Configuration

    @property
    def keeps_loaded_context_at_cut(self) -> bool:
        return self.configuration is Configuration.SOURCE_ONLY

    @property
    def admits_post_cut_source(self) -> bool:
        return self.configuration is Configuration.IGNORE_INFO_CHECKS

    @property
    def gates_export(self) -> bool:
        return self.configuration is not Configuration.UNGUARDED_EXPORT

    @property
    def deletes_evidence(self) -> bool:
        return self.configuration is Configuration.DELETE_EVIDENCE

    @property
    def checks_grant(self) -> bool:
        return self.configuration is not Configuration.IGNORE_GRANT_CHECKS

    @property
    def release_timing_depends_on_secret(self) -> bool:
        return self.configuration is Configuration.TIMED_RELEASE


def policy_for(configuration: Configuration | str) -> Policy:
    return Policy(Configuration(configuration))
