# TLA+ model

`modules/AuditPreservingRevocation.tla` is an independently maintained finite reference specification. It includes the three per-source actions (`Read`, `Derive`, `Load`), all 17 global actions, the `InfoSafe`, `AuthSafe`, and `ReviewAvailable` predicates, and the seven configuration switches. `AuditPreservingRevocationProduct.tla` gives the synchronized two-secret observation product, including the complete release-position comparison and payload-only comparison. `Base.tla` and `Actions.tla` retain shared vocabulary modules.

The supplied manuscript did not include its original modules, so these files are an independent reconstructed implementation rather than a claim that the missing 147-line source has been recovered. The actual line counts should be reported with the final release.

Run it with a local TLC distribution:

```text
set TLA2TOOLS_JAR=C:\path\to\tla2tools.jar
python scripts/run_tlc.py
```

The generated log is stored under `results/logs/`. No TLC jar is bundled or downloaded by this repository.
