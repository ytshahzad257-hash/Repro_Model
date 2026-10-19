"""Deterministic synthetic CLR quarantine experiment."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, asdict
from statistics import mean, stdev

from .labels import Label, LabeledItem, join, reachable_quarantine


@dataclass(frozen=True, slots=True)
class WorkflowMetrics:
    quarantined: float
    truly_dependent: float
    over_quarantine_ratio: float | None
    withheld_clean: float
    sound: bool


def _half_width(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * stdev(values) / math.sqrt(len(values))


def simulate_workflow(*, sources: int, derived: int, restricted_probability: float, fanin: int, use_probability: float, seed: int,
                      selection: str = "uniform", use_model: str = "independent") -> WorkflowMetrics:
    """Simulate one workflow with explicit, local pseudorandom state."""

    # Common random numbers: the workflow graph depends only on ``seed``, and
    # each admitted edge draws one uniform from a separate stream, used iff it
    # is below ``use_probability``.  Workflows are therefore paired across u
    # and their true-dependence sets are nested as u grows.
    rng = random.Random(seed)
    use_rng = random.Random(seed * 2_654_435_761 % (2**61 - 1) + 17)
    if selection not in {"uniform","recency","zipf"} or use_model not in {"independent","correlated","first_only"}:
        raise ValueError("Unknown selection or use model")
    restricted = {i for i in range(sources) if rng.random() < restricted_probability}
    if not restricted:
        restricted.add(rng.randrange(sources))
    labels: list[Label] = [frozenset({f"s{i}"}) for i in range(sources)]
    dependence: list[frozenset[int]] = [frozenset({i}) for i in range(sources)]
    items: list[LabeledItem] = []
    true_masks: list[frozenset[int]] = []
    for item_index in range(derived):
        candidates = list(range(sources + item_index))
        # Section 7.5: item c_j admits between one and F inputs, drawn
        # uniformly without replacement from the sources and earlier items.
        admitted_count = rng.randint(1, fanin)
        if selection == "uniform":
            selected = rng.sample(candidates, k=min(admitted_count, len(candidates)))
        else:
            weights=[0.9 ** (sources+item_index-1-i) if selection=="recency" else (i+1) ** -1.1 for i in candidates]
            selected=[]
            for _ in range(min(admitted_count,len(candidates))):
                chosen=rng.choices(range(len(candidates)),weights=weights,k=1)[0]
                selected.append(candidates.pop(chosen));weights.pop(chosen)
        admitted_labels: list[Label] = []
        admitted_dep: list[frozenset[int]] = []
        for candidate in selected:
            if candidate < sources:
                admitted_labels.append(labels[candidate])
                admitted_dep.append(dependence[candidate])
            else:
                prior = candidate - sources
                admitted_labels.append(items[prior].label)
                admitted_dep.append(true_masks[prior])
        if use_model == "first_only":
            used=[0] if selected else []
        elif use_model == "correlated" and use_rng.random() < 0.5:
            used=list(range(len(selected)))
        else:
            used = [index for index in range(len(selected)) if use_rng.random() < use_probability]
        # CLR labels conservatively propagate every admitted input. The kernel's
        # actual use is sampled separately for ground truth.
        label = join(*admitted_labels) if admitted_labels else frozenset()
        dep = frozenset(value for index in used for value in admitted_dep[index])
        item = LabeledItem(f"d{item_index}", item_index, label)
        items.append(item)
        true_masks.append(dep)
    prohibited = frozenset(f"s{i}" for i in restricted)
    quarantined_ids = reachable_quarantine(items, prohibited)
    quarantined = [item.identifier in quarantined_ids for item in items]
    true = [bool(dep & restricted) for dep in true_masks]
    q_count = sum(quarantined)
    true_count = sum(true)
    clean_withheld = sum(q and not t for q, t in zip(quarantined, true))
    # The over-quarantine ratio is defined only when something is quarantined.
    ratio = (clean_withheld / q_count) if q_count else None
    return WorkflowMetrics(
        quarantined=q_count / derived,
        truly_dependent=true_count / derived,
        over_quarantine_ratio=ratio,
        withheld_clean=clean_withheld / derived,
        sound=all(not t or q for t, q in zip(true, quarantined)),
    )


def run_quarantine_experiment(
    *, seeds: list[int], use_probabilities: tuple[float, ...] = (0.10, 0.25, 0.50, 0.75, 1.0),
    sources: int = 100, derived: int = 20, restricted_probability: float = 0.1, fanin: int = 3,
    selection: str = "uniform", use_model: str = "independent",
    raw_records: list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for use_probability in use_probabilities:
        metrics = [
            simulate_workflow(
                sources=sources,
                derived=derived,
                restricted_probability=restricted_probability,
                fanin=fanin,
                use_probability=use_probability,
                seed=seed,
                selection=selection,use_model=use_model,
            )
            for seed in seeds
        ]
        if raw_records is not None:
            raw_records.extend({"seed": seed, "use_probability": use_probability, **asdict(metric)}
                               for seed, metric in zip(seeds, metrics))
        row: dict[str, object] = {"use_probability": use_probability, "workflows": len(metrics)}
        for field in ("quarantined", "truly_dependent", "over_quarantine_ratio", "withheld_clean"):
            values = [getattr(metric, field) for metric in metrics if getattr(metric, field) is not None]
            row[field] = mean(values)
            row[f"{field}_half_width"] = _half_width(values)
        row["workflows_with_quarantine"] = sum(metric.over_quarantine_ratio is not None for metric in metrics)
        row["soundness_failures"] = sum(not metric.sound for metric in metrics)
        rows.append(row)
    return rows
