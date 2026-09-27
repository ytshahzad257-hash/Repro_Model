"""Run Algorithm 1 for the recorder/question matrix."""

from __future__ import annotations

import json
from dataclasses import dataclass

from apr.sufficiency import FiniteLTS, LabeledStep, RecorderMachine, decide_sufficiency

from common import GENERATED, load_seeds, provenance, write_csv, write_json, write_latex, write_markdown


@dataclass(frozen=True)
class History:
    actions: tuple[str, ...]
    admission: int
    order: int
    final_state: int
    causal: int


def histories() -> tuple[History, ...]:
    rows: list[History] = []
    for admission in (0, 1):
        for order in (0, 1):
            for final_state in (0, 1):
                for causal in (0, 1):
                    # Causal is intentionally not encoded in the mediator path.
                    rows.append(History(
                        actions=(
                            "Receipt",
                            "OrderA" if order == 0 else "OrderB",
                            "Admitted" if admission else "NotAdmitted",
                            "FinalA" if final_state == 0 else "FinalB",
                        ),
                        admission=admission,
                        order=order,
                        final_state=final_state,
                        causal=causal,
                    ))
    return tuple(rows)


def build_lts() -> tuple[FiniteLTS[int], dict[int, History]]:
    hs = histories()
    transitions: dict[int, list[LabeledStep[int]]] = {}
    answers: dict[int, History] = {}
    next_state = 1
    for history in hs:
        current = 0
        for action in history.actions:
            state = next_state
            next_state += 1
            transitions.setdefault(current, []).append(LabeledStep(action, action, state))
            current = state
        transitions.setdefault(current, [])
        answers[current] = history
    finals = frozenset(answers)

    def answer(state: int, _history: tuple[str, ...]) -> object:
        return answers[state]

    # Each final state exposes all question answers. A question selector below
    # projects the tuple; this keeps Algorithm 1's LTS generic.
    return FiniteLTS(0, finals, {key: tuple(value) for key, value in transitions.items()}, answer), answers


def question_answer(history: History, name: str) -> int:
    return {"admission": history.admission, "order": history.order, "causal": history.causal}[name]


def recorder(name: str) -> RecorderMachine:
    if name == "receipts":
        allowed = {"Receipt", "OrderA", "OrderB"}
    elif name == "admission_ledger_only":
        allowed = {"Admitted", "NotAdmitted"}
    elif name == "receipts_plus_admission_ledger":
        allowed = {"Receipt", "OrderA", "OrderB", "Admitted", "NotAdmitted"}
    elif name == "full_mediator_log":
        allowed = {"Receipt", "OrderA", "OrderB", "Admitted", "NotAdmitted", "FinalA", "FinalB"}
    else:
        raise KeyError(name)
    return RecorderMachine(lambda action: action if action in allowed else None)


def run() -> list[dict[str, object]]:
    lts, answer_states = build_lts()
    rows: list[dict[str, object]] = []
    witnesses: dict[str, object] = {}
    for recorder_name in ("receipts", "admission_ledger_only", "receipts_plus_admission_ledger", "full_mediator_log"):
        for question_name in ("admission", "order", "causal"):
            selected_lts = FiniteLTS(
                lts.initial,
                lts.finals,
                lts.transitions,
                lambda state, _history, q=question_name: question_answer(answer_states[state], q),
            )
            result = decide_sufficiency(selected_lts, recorder(recorder_name))
            row = {
                "recorder": recorder_name,
                "question": question_name,
                "verdict": "sufficient" if result.sufficient else "insufficient",
                "explored_product_nodes": result.explored_nodes,
            }
            rows.append(row)
            if not result.sufficient:
                witnesses[f"{recorder_name}_{question_name}"] = {
                    "history": list(result.left_history or ()),
                    "history_prime": list(result.right_history or ()),
                    "answer": result.left_answer,
                    "answer_prime": result.right_answer,
                    "explanation": "The recorder outputs are equal, but the selected question answers differ.",
                }
    metadata = provenance(experiment="table6_algorithm1", inputs={"histories": len(histories())}, seed=load_seeds().get("algorithm"))
    write_json(GENERATED / "table6.json", {"rows": rows, "metadata": metadata})
    write_csv(GENERATED / "table6.csv", rows)
    write_markdown(GENERATED / "table6.md", rows)
    write_latex(GENERATED / "table6.tex", rows)
    write_json(GENERATED / "table6.metadata.json", metadata)
    for key, value in witnesses.items():
        write_json(GENERATED / "witnesses" / f"{key}.json", value)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
