"""Table 6: Algorithm 1 on the pre-cut Governed model.

The kernel is modelled by a hidden choice at each admission: Load[i] is split
into Load[i]/use and Load[i]/ignore, which are identical at the mediator but
differ in whether the admitted content influenced the output.  Questions are
deterministic automata folded into the state:
  admission -- the set of sources admitted to the working context;
  order     -- the order of the cut obligations Isolate, Fence, Persist, CommitCut;
  causal    -- whether some admitted restricted input was actually used.
"""

from __future__ import annotations

from .model import TransitionSystem
from .policies import Configuration
from .question_bounds import ORDER_EVENTS
from .sufficiency import GenericResult, decide_generic

RECEIPT_EVENTS = frozenset({"RequestRevoke", "UpdatePolicy", "Isolate", "Fence", "Persist", "CommitCut", "PrepareEffect", "FireEffect"})

RECORDERS = ("receipts", "admission_ledger", "receipts_plus_admission_ledger", "full_mediator_log")
QUESTIONS = ("admission", "order", "causal")


def mediator_view(action: str) -> str:
    return action.split("/")[0]


def token_function(recorder: str):
    def receipts(action: str):
        return action if action in RECEIPT_EVENTS else None

    def ledger(action: str):
        base = mediator_view(action)
        return base if base.startswith("Load[") else None

    if recorder == "receipts":
        return receipts
    if recorder == "admission_ledger":
        return ledger
    if recorder == "receipts_plus_admission_ledger":
        return lambda a: receipts(a) or ledger(a)
    if recorder == "full_mediator_log":
        return mediator_view
    raise KeyError(recorder)


def build(sources: int, question: str):
    system = TransitionSystem(Configuration.GOVERNED, sources=sources)

    def successors(node):
        state, aux = node
        for transition in system.transitions(state):
            action, target = transition.action, transition.target
            if action.startswith("Load["):
                index = int(action[5:-1])
                for mode in ("use", "ignore"):
                    yield f"{action}/{mode}", (target, _update(question, aux, action, index, mode))
            else:
                yield action, (target, _update(question, aux, action, None, None))

    initial = (system.initial(0), _initial(question))
    return initial, successors, (lambda node: system.is_completion(node[0])), (lambda node: node[1])


def _initial(question: str):
    return {"admission": 0, "order": (), "causal": False}[question]


def _update(question: str, aux, action: str, index, mode):
    if question == "admission" and index is not None:
        return aux | (1 << index)
    if question == "order" and action in ORDER_EVENTS:
        return aux + (action,)
    if question == "causal" and mode == "use":
        return True
    return aux


def run_matrix(sources: int) -> list[dict[str, object]]:
    rows = []
    for recorder in RECORDERS:
        for question in QUESTIONS:
            initial, successors, is_final, answer = build(sources, question)
            result: GenericResult = decide_generic(initial, successors, is_final, answer, token_function(recorder))
            rows.append({
                "sources": sources,
                "recorder": recorder,
                "question": question,
                "verdict": "sufficient" if result.sufficient else "insufficient",
                "explored_product_nodes": result.explored_nodes,
                "witness_left": None if result.sufficient else list(result.left_history),
                "witness_right": None if result.sufficient else list(result.right_history),
                "answer_left": None if result.sufficient else repr(result.left_answer),
                "answer_right": None if result.sufficient else repr(result.right_answer),
            })
    return rows
