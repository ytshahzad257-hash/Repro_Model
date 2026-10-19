---- MODULE AuditPreservingRevocation ----
EXTENDS Naturals, FiniteSets
CONSTANT Secret, Config

VARIABLES phase, read, derived, loaded, effectPrepared, effectFired,
          requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
          reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
          deliberated, publicReconstructed, grantRevoked, used,
          infoViolation, authViolation, evidenceDeleted

vars == <<phase, read, derived, loaded, effectPrepared, effectFired,
           requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
           reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
           deliberated, publicReconstructed, grantRevoked, used,
           infoViolation, authViolation, evidenceDeleted>>

ConfigSet == {"Governed", "SourceOnly", "IgnoreInfoChecks", "UnguardedExport",
              "DeleteEvidence", "IgnoreGrantChecks", "TimedRelease"}

Init ==
  /\ Secret \in {0, 1}
  /\ Config \in ConfigSet
  /\ phase = 0
  /\ read = FALSE
  /\ derived = FALSE
  /\ loaded = FALSE
  /\ effectPrepared = FALSE
  /\ effectFired = FALSE
  /\ requestRevoke = FALSE
  /\ policyUpdated = FALSE
  /\ isolated = FALSE
  /\ fenced = FALSE
  /\ persisted = FALSE
  /\ committed = FALSE
  /\ reviewOpen = FALSE
  /\ reportGenerated = FALSE
  /\ reviewAnswered = FALSE
  /\ reportExported = FALSE
  /\ released = FALSE
  /\ deliberated = FALSE
  /\ publicReconstructed = FALSE
  /\ grantRevoked = FALSE
  /\ used = FALSE
  /\ infoViolation = FALSE
  /\ authViolation = FALSE
  /\ evidenceDeleted = FALSE

Read ==
  /\ ~read /\ ~isolated
  /\ read' = TRUE
  /\ UNCHANGED <<phase, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Derive ==
  /\ read /\ ~derived
  /\ derived' = TRUE
  /\ UNCHANGED <<phase, read, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Load ==
  /\ derived /\ ~loaded
  /\ ~isolated \/ Config = "IgnoreInfoChecks"
  /\ loaded' = TRUE
  /\ UNCHANGED <<phase, read, derived, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

PrepareEffect ==
  /\ loaded /\ ~effectPrepared /\ ~committed
  /\ effectPrepared' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

RequestRevoke ==
  /\ loaded /\ ~requestRevoke /\ ~committed
  /\ requestRevoke' = TRUE /\ phase' = 1
  /\ UNCHANGED <<read, derived, loaded, effectPrepared, effectFired,
                   policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

UpdatePolicy ==
  /\ requestRevoke /\ ~policyUpdated
  /\ policyUpdated' = TRUE /\ phase' = 2
  /\ UNCHANGED <<read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Isolate ==
  /\ policyUpdated /\ ~isolated
  /\ isolated' = TRUE
  /\ loaded' = IF Config = "SourceOnly" THEN loaded ELSE FALSE
  /\ evidenceDeleted' = Config = "DeleteEvidence"
  /\ phase' = 3
  /\ UNCHANGED <<read, derived, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation>>

Fence ==
  /\ policyUpdated /\ ~fenced
  /\ fenced' = TRUE /\ phase' = 4
  /\ UNCHANGED <<read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Persist ==
  /\ isolated /\ fenced /\ ~persisted
  /\ persisted' = TRUE /\ phase' = 5
  /\ UNCHANGED <<read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

CommitCut ==
  /\ isolated /\ fenced /\ persisted /\ ~committed
  /\ committed' = TRUE /\ phase' = 6
  /\ UNCHANGED <<read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

OpUse ==
  /\ committed /\ ~used
  /\ loaded \/ publicReconstructed \/ released \/ (Config = "UnguardedExport" /\ reportExported)
  /\ used' = TRUE /\ infoViolation' = infoViolation \/ loaded
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked,
                   authViolation, evidenceDeleted>>

FireEffect ==
  /\ effectPrepared /\ fenced /\ ~effectFired
  /\ effectFired' = TRUE
  /\ authViolation' = authViolation \/ (grantRevoked /\ Config = "IgnoreGrantChecks")
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, evidenceDeleted>>

Review ==
  /\ committed /\ ~reviewOpen
  /\ reviewOpen' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

GenerateReport ==
  /\ reviewOpen /\ ~reportGenerated
  /\ reportGenerated' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Answer ==
  /\ reportGenerated /\ ~reviewAnswered /\ ~evidenceDeleted
  /\ reviewAnswered' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reportExported, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

ReportExport ==
  /\ reviewAnswered /\ ~reportExported
  /\ reportExported' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, released,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

Release ==
  /\ reportGenerated \/ reportExported
  /\ ~released /\ Config # "UnguardedExport"
  /\ released' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported,
                   deliberated, publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

PrivateDeliberation ==
  /\ committed /\ ~deliberated
  /\ deliberated' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   publicReconstructed, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

CleanPublicReconstruct ==
  /\ committed /\ ~publicReconstructed
  /\ publicReconstructed' = TRUE /\ loaded' = FALSE
  /\ UNCHANGED <<phase, read, derived, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, grantRevoked, used,
                   infoViolation, authViolation, evidenceDeleted>>

GrantRevoke ==
  /\ committed /\ ~grantRevoked
  /\ grantRevoked' = TRUE
  /\ UNCHANGED <<phase, read, derived, loaded, effectPrepared, effectFired,
                   requestRevoke, policyUpdated, isolated, fenced, persisted, committed,
                   reviewOpen, reportGenerated, reviewAnswered, reportExported, released,
                   deliberated, publicReconstructed, used,
                   infoViolation, authViolation, evidenceDeleted>>

Next == Read \/ Derive \/ Load \/ PrepareEffect \/ RequestRevoke \/ UpdatePolicy
        \/ Isolate \/ Fence \/ Persist \/ CommitCut \/ OpUse \/ FireEffect
        \/ Review \/ GenerateReport \/ Answer \/ ReportExport \/ Release
        \/ PrivateDeliberation \/ CleanPublicReconstruct \/ GrantRevoke

InfoSafe == ~infoViolation
AuthSafe == ~authViolation
ReviewAvailable == ~evidenceDeleted
Spec == Init /\ [][Next]_vars

====
