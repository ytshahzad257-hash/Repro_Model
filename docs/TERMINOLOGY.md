# Terminology

The software uses the following technical terminology.

| Term | Meaning in the artifact |
| --- | --- |
| source | A restricted representation with a one-bit secret value |
| derived item | A summary or representation derived from a source |
| admission | Loading a derived representation into operational context |
| effective cut | The committed revocation boundary after update, isolation, fencing, and persistence |
| quarantine | Keeping restricted residue in evidence while removing it from operational context |
| evidence | Retained private state used by the review service |
| review | The protected sequence that opens evidence, generates a report, and answers |
| approved release | A release-gated public view of a review artifact |
| complete observation | Payload, refusal, metadata, and logical release position declared by the contract |
| payload-only observation | Complete observation with logical release position removed |
| information safety | No post-cut operational use of prohibited information |
| authorization safety | No effect accepted after the selected grant support is revoked |
| question-relative sufficiency | Evidence factorization through the declared question family |
| CLR | Compartmentalized label runtime; the conservative label/quarantine mechanism |
