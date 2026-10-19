# TLA+ model

`modules/AuditPreservingRevocation.tla` is an independently maintained finite reference specification. It includes the three per-source actions (`Read`, `Derive`, `Load`), all 17 global actions, the `InfoSafe`, `AuthSafe`, and `ReviewAvailable` predicates, and the seven configuration switches. `AuditPreservingRevocationProduct.tla` gives the synchronized two-secret observation product, including the complete release-position comparison and payload-only comparison. `Base.tla` and `Actions.tla` retain shared vocabulary modules.

The original modules were not preserved, so these files are an independent reconstruction rather than a recovery of the earlier source. They are retained for reference and are not used by the current checks.

Run it with a local TLC distribution:

```text
set TLA2TOOLS_JAR=C:\path\to\tla2tools.jar
python scripts/run_tlc.py
```

The generated log is stored under `results/logs/`. No TLC jar is bundled or downloaded by this repository.
