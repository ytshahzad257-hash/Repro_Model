"""Declared experiment inputs only; no transition or property semantics."""
CONFIGS = ("Governed", "SourceOnly", "IgnoreInfoChecks", "UnguardedExport",
           "DeleteEvidence", "IgnoreGrantChecks", "TimedRelease",
           "ApprovedSecretRelease", "RefusalMutation")

def cases(max_k=4, independent=True, larger=True):
    result=[]
    for k in range(1,max_k+1):
        for cfg in CONFIGS:
            result.append(dict(case_id=f"{cfg}/K{k}",configuration=cfg,sources=k,
                               secrets="shared",revocation="all",revoked=list(range(k)),left=0,right=1))
    if independent:
        for k in range(1,4):
            left=sum((i%2)<<i for i in range(k))
            for pattern in ("one","all"):
                revoked=[0] if pattern=="one" else list(range(k))
                right=left ^ sum(1<<i for i in revoked)
                for cfg in CONFIGS:
                    result.append(dict(case_id=f"{cfg}/K{k}/independent/{pattern}",configuration=cfg,
                                       sources=k,secrets="independent",revocation=pattern,
                                       revoked=revoked,left=left,right=right))
    if larger:
        for cfg in CONFIGS:
            result.append(dict(case_id=f"{cfg}/K5",configuration=cfg,sources=5,
                               secrets="shared",revocation="all",revoked=list(range(5)),left=0,right=1))
    return result
