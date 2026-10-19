-------------------------------- MODULE APR --------------------------------
(* Single-copy model for one value of the one-bit secret.                  *)
EXTENDS APRSemantics
CONSTANT SECRET
VARIABLE s

Init == s = InitState(SECRET)
Next == \E a \in PublicActs \cup InternalActs : Step(a, s, s')
Spec == Init /\ [][Next]_s

InfoSafe       == ~s.uInfo
AuthSafe       == ~s.uAuth
(* In this model a committed state can still reach an answered review iff *)
(* its evidence was not deleted; the Python explorer checks the general   *)
(* reachability form of ReviewAvailable.                                  *)
ReviewPossible == s.committed => ~s.evDeleted
=============================================================================
