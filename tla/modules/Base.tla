---- MODULE Base ----
EXTENDS Naturals, FiniteSets

Configs == {"Governed", "SourceOnly", "IgnoreInfoChecks", "UnguardedExport",
            "DeleteEvidence", "IgnoreGrantChecks", "TimedRelease"}

Bool == {TRUE, FALSE}

====
