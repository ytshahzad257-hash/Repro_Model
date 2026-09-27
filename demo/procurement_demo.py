"""Small deterministic illustration of the procurement scenario.

This is an executable illustration of the R1-R8 discipline, not a production
LLM evaluation or an empirical deployment study.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str
    payload: str
    label: frozenset[str]


def main() -> None:
    price = Item("supplier-price", "confidential: 42", frozenset({"supplier-v1"}))
    summary = Item("summary", "supplier price is 42", price.label)
    plan = Item("purchasing-plan", "buy 10 units", summary.label)
    print("admit", price.name, "->", summary.name, "->", plan.name)
    print("queue", "purchase-order", "then revoke")
    print("cut", "policy-update", "isolate", "fence", "persist", "commit")
    print("quarantine", summary.name, plan.name)
    print("rebuild", "public context only")
    print("post-cut reuse", "denied")
    print("review", "authorized investigator confirms admission")
    print("release", "bounded public finding: restricted context was admitted")


if __name__ == "__main__":
    main()
