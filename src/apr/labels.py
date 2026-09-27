"""Label and quarantine helpers for the compartmentalized label runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable


Tag = str
Label = FrozenSet[Tag]


def join(*labels: Iterable[Tag]) -> Label:
    """Return the immutable union of labels."""

    return frozenset(tag for label in labels for tag in label)


def is_free(label: Label, prohibited: Label) -> bool:
    """Whether a label is disjoint from the prohibited source set."""

    return label.isdisjoint(prohibited)


@dataclass(frozen=True)
class LabeledItem:
    """A derived item with conservative dependency metadata."""

    identifier: str
    payload: object
    label: Label


def reachable_quarantine(items: Iterable[LabeledItem], prohibited: Label) -> frozenset[str]:
    """Return identifiers whose conservative labels meet the prohibited set."""

    return frozenset(item.identifier for item in items if not is_free(item.label, prohibited))
