----------------------------- MODULE APRProduct -----------------------------
(* Synchronous self-composition of the s=0 and s=1 copies.  Public actions *)
(* are taken jointly; internal actions are taken by one copy alone and     *)
(* change the logical-position lag between the copies.                     *)
EXTENDS APRSemantics, Integers
CONSTANTS LEFT, RIGHT, EQRELEASE
VARIABLES sl, sr, lag
vars == <<sl, sr, lag>>

Init  == /\ lag = 0
         /\ IF EQRELEASE /\ ApprovedSecret
               THEN \E v \in {LEFT, RIGHT} : sl = InitState(v) /\ sr = InitState(v)
               ELSE sl = InitState(LEFT) /\ sr = InitState(RIGHT)
Joint == \E a \in PublicActs : Step(a, sl, sl') /\ Step(a, sr, sr') /\ lag' = lag
SoloL == \E a \in InternalActs : Step(a, sl, sl') /\ sr' = sr /\ lag' = lag + 1
SoloR == \E a \in InternalActs : Step(a, sr, sr') /\ sl' = sl /\ lag' = lag - 1
Next  == Joint \/ SoloL \/ SoloR
Spec  == Init /\ [][Next]_vars

(* Full observation: kind, payload and logical position must agree. *)
ObsEqualStep     == /\ Obs(sl, sl') = Obs(sr, sr')
                    /\ Obs(sl, sl')[1] # "none" => lag = 0
(* Payload-only observation: logical position discarded. *)
PayloadEqualStep == Obs(sl, sl') = Obs(sr, sr')

(* A public request enabled in one copy and refused in the other is an    *)
(* observable refusal; complete observations require equal enabledness.   *)
EnabledEqual == \A a \in PublicActs : En(a, sl) = En(a, sr)

ObsEqual     == [][ObsEqualStep]_vars
PayloadEqual == [][PayloadEqualStep]_vars
=============================================================================
