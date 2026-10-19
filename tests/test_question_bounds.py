from collections import defaultdict

from apr.question_bounds import ORDER_EVENTS, compute, enumerate_histories, in_view


def test_dynamic_programme_matches_brute_force_for_k1():
    fibers = defaultdict(list)
    for history, final in enumerate_histories(1):
        view = tuple(a for a in history if in_view(a))
        adm = 1 if any(a.startswith("Load[") for a in history) else 0
        order = tuple(a for a in history if a in ORDER_EVENTS)
        fibers[view].append((history, adm, order, final))
    bounds = compute(1)
    assert bounds.histories == sum(len(v) for v in fibers.values())
    assert bounds.fibers == len(fibers)
    assert bounds.max_fiber_histories == max(len(v) for v in fibers.values())
    assert bounds.admission_classes == max(len({x[1] for x in v}) for v in fibers.values())
    assert bounds.order_classes == max(len({x[2] for x in v}) for v in fibers.values())
    assert bounds.final_state_classes == max(len({x[3] for x in v}) for v in fibers.values())


def test_admission_class_meets_corollary_1():
    for k in (1, 2):
        assert compute(k).admission_classes == 2 ** k
