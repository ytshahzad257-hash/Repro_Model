---------------------------- MODULE APRSemantics ----------------------------
(***************************************************************************)
(* Shared action semantics of the audit-preserving revocation model,      *)
(* parametric in the number K of restricted sources and in the named      *)
(* configuration CFG.  A state is one record; Step(a, s, t) holds when    *)
(* action a is enabled in s and t is its successor.  This module is a     *)
(* second, separately written encoding of the semantics fixed in          *)
(* docs/FORMAL_MODEL.md; it shares no code with the Python explorer.      *)
(***************************************************************************)
EXTENDS Naturals

CONSTANTS K, CFG, MODE, REVOKED, CACHE

Src == 1..K

KeepsLoadedAtCut == CFG = "SourceOnly"
AdmitsPostCut    == CFG = "IgnoreInfoChecks"
GatesExport      == CFG # "UnguardedExport"
DeletesEvidence  == CFG = "DeleteEvidence"
ChecksGrant      == CFG # "IgnoreGrantChecks"
TimedRelease     == CFG = "TimedRelease"
ApprovedSecret  == CFG = "ApprovedSecretRelease"
RefusalMutation == CFG = "RefusalMutation"

NoSrc == [i \in Src |-> FALSE]

InitState(sec) ==
  [ secret |-> sec, read |-> NoSrc, derived |-> NoSrc, loaded |-> NoSrc, cache |-> NoSrc,
    reqRevoke |-> FALSE, polUpd |-> FALSE, isolated |-> FALSE,
    fenced |-> FALSE, persisted |-> FALSE, committed |-> FALSE,
    effPrep |-> FALSE, effFired |-> FALSE, grantRev |-> FALSE,
    revOpen |-> FALSE, repGen |-> FALSE, answered |-> FALSE,
    exported |-> FALSE, released |-> FALSE, relDelayed |-> FALSE,
    deliberated |-> FALSE, pubRecon |-> FALSE, evDeleted |-> FALSE,
    opUses |-> 0, uInfo |-> FALSE, uAuth |-> FALSE ]

HasLoaded(s)    == \E i \in Src : s.loaded[i]
HasMemory(s)    == \E i \in Src : s.loaded[i] \/ s.cache[i]
HasRestricted(s) == s.exported \/ (\E i \in REVOKED : s.loaded[i] \/ s.cache[i])
FirstRevoked == CHOOSE i \in REVOKED : \A j \in REVOKED : i <= j
Bit(s, i) == IF MODE = "shared" THEN s.secret ELSE (s.secret \div (2^(i-1))) % 2
ClearRevoked(items) == [i \in Src |-> IF i \in REVOKED THEN FALSE ELSE items[i]]
ReleasePayload(s) == IF ApprovedSecret THEN s.secret ELSE 0
MemoryPayload(s) == IF MODE = "shared" THEN s.secret
                    ELSE [i \in Src |-> IF s.loaded[i] \/ s.cache[i] THEN Bit(s,i) ELSE 0]
UsePayload(s) == IF s.exported THEN s.secret
                 ELSE IF HasMemory(s) THEN MemoryPayload(s)
                 ELSE IF s.released THEN ReleasePayload(s) ELSE 0
ReleaseReady(s) == GatesExport /\ s.repGen /\ ~s.released

GlobalNames == {"PrepareEffect", "RequestRevoke", "UpdatePolicy", "Isolate",
                "Fence", "Persist", "CommitCut", "OpUse", "FireEffect",
                "Review", "GenerateReport", "Answer", "ReportExport",
                "Release", "PrivateDeliberation", "CleanPublicReconstruct",
                "GrantRevoke"}

PublicActs   == ({"Read", "Derive", "Load"} \X Src) \cup (GlobalNames \X {0})
InternalActs == {<<"DelayRelease", 0>>}

(* En(a, s): action a is enabled in s (a Boolean state predicate).          *)
En(a, s) ==
  LET n == a[1]
      i == a[2]
  IN CASE n = "Read"          -> (i \notin REVOKED \/ ~s.polUpd \/ AdmitsPostCut) /\ ~s.read[i]
       [] n = "Derive"        -> (i \notin REVOKED \/ ~s.isolated \/ AdmitsPostCut) /\ s.read[i] /\ ~s.derived[i]
       [] n = "Load"          -> (i \notin REVOKED \/ ~s.isolated \/ AdmitsPostCut) /\ s.derived[i] /\ ~s.loaded[i]
       [] n = "PrepareEffect" -> HasLoaded(s) /\ ~s.effPrep /\ ~s.fenced
       [] n = "RequestRevoke" -> ~s.reqRevoke /\ ~s.committed
       [] n = "UpdatePolicy"  -> s.reqRevoke /\ ~s.polUpd
       [] n = "Isolate"       -> s.polUpd /\ ~s.isolated
       [] n = "Fence"         -> s.polUpd /\ ~s.fenced
       [] n = "Persist"       -> s.isolated /\ s.fenced /\ ~s.persisted
       [] n = "CommitCut"     -> s.isolated /\ s.fenced /\ s.persisted /\ ~s.committed
       [] n = "OpUse"         -> /\ s.committed /\ s.opUses = 0
                                 /\ ~(RefusalMutation /\ Bit(s, FirstRevoked) = 1)
                                 /\ ~(s.grantRev /\ ChecksGrant)
                                 /\ (HasMemory(s) \/ s.exported \/ s.released \/ s.pubRecon)
       [] n = "FireEffect"    -> s.effPrep /\ ~s.effFired /\ ~s.fenced
       [] n = "Review"        -> s.committed /\ s.persisted /\ ~s.revOpen
       [] n = "GenerateReport" -> s.revOpen /\ ~s.repGen
       [] n = "Answer"        -> s.repGen /\ ~s.answered /\ ~s.evDeleted
       [] n = "ReportExport"  -> ~GatesExport /\ s.answered /\ ~s.exported
       [] n = "Release"       -> ReleaseReady(s) /\ ((TimedRelease /\ Bit(s,FirstRevoked) = 1) => s.relDelayed)
       [] n = "PrivateDeliberation" -> s.committed /\ ~s.deliberated
       [] n = "CleanPublicReconstruct" -> s.committed /\ ~s.pubRecon
       [] n = "GrantRevoke"   -> s.committed /\ ~s.grantRev
       [] n = "DelayRelease"  -> TimedRelease /\ Bit(s,FirstRevoked) = 1 /\ ReleaseReady(s) /\ ~s.relDelayed

(* Succ(a, s): the successor of s under a (meaningful when En(a, s)).      *)
Succ(a, s) ==
  LET n == a[1]
      i == a[2]
  IN CASE n = "Read"          -> [s EXCEPT !.read[i] = TRUE]
       [] n = "Derive"        -> [s EXCEPT !.derived[i] = TRUE]
       [] n = "Load"          -> [s EXCEPT !.loaded[i] = TRUE, !.cache[i] = IF CACHE THEN TRUE ELSE @]
       [] n = "PrepareEffect" -> [s EXCEPT !.effPrep = TRUE]
       [] n = "RequestRevoke" -> [s EXCEPT !.reqRevoke = TRUE]
       [] n = "UpdatePolicy"  -> [s EXCEPT !.polUpd = TRUE]
       [] n = "Isolate"       -> [s EXCEPT !.isolated = TRUE,
                                           !.loaded = IF KeepsLoadedAtCut THEN s.loaded ELSE ClearRevoked(s.loaded),
                                           !.cache = IF KeepsLoadedAtCut THEN s.cache ELSE ClearRevoked(s.cache),
                                           !.evDeleted = DeletesEvidence]
       [] n = "Fence"         -> [s EXCEPT !.fenced = TRUE]
       [] n = "Persist"       -> [s EXCEPT !.persisted = TRUE]
       [] n = "CommitCut"     -> [s EXCEPT !.committed = TRUE]
       [] n = "OpUse"         -> [s EXCEPT !.opUses = 1,
                                           !.uInfo = s.uInfo \/ HasRestricted(s),
                                           !.uAuth = s.uAuth \/ (s.grantRev /\ ~ChecksGrant)]
       [] n = "FireEffect"    -> [s EXCEPT !.effFired = TRUE]
       [] n = "Review"        -> [s EXCEPT !.revOpen = TRUE]
       [] n = "GenerateReport" -> [s EXCEPT !.repGen = TRUE]
       [] n = "Answer"        -> [s EXCEPT !.answered = TRUE]
       [] n = "ReportExport"  -> [s EXCEPT !.exported = TRUE]
       [] n = "Release"       -> [s EXCEPT !.released = TRUE]
       [] n = "PrivateDeliberation" -> [s EXCEPT !.deliberated = TRUE]
       [] n = "CleanPublicReconstruct" -> [s EXCEPT !.pubRecon = TRUE, !.loaded = NoSrc]
       [] n = "GrantRevoke"   -> [s EXCEPT !.grantRev = TRUE]
       [] n = "DelayRelease"  -> [s EXCEPT !.relDelayed = TRUE]

(* The guard is evaluated as a value inside IF, so TLC generates exactly   *)
(* one successor per enabled action (no splitting of guard disjunctions).  *)
Step(a, s, t) == IF En(a, s) THEN t = Succ(a, s) ELSE FALSE

(* Observation emitted by the step s -> t, as seen by the former beneficiary. *)
Obs(s, t) ==
  IF t.opUses # s.opUses
    THEN <<"use", UsePayload(s)>>
  ELSE IF t.released # s.released THEN <<"release", ReleasePayload(s)>>
  ELSE IF t.effFired # s.effFired THEN <<"effect", 0>>
  ELSE <<"none", 0>>
=============================================================================
