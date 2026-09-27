---- MODULE AuditPreservingRevocationProduct ----
EXTENDS Naturals
CONSTANT SecretLeft, SecretRight, Config

VARIABLES leftStep, rightStep, leftReleased, rightReleased,
          leftPayload, rightPayload, leftReleasePosition, rightReleasePosition

vars == <<leftStep, rightStep, leftReleased, rightReleased,
           leftPayload, rightPayload, leftReleasePosition, rightReleasePosition>>

ProductInit ==
  /\ SecretLeft \in {0, 1}
  /\ SecretRight \in {0, 1}
  /\ Config # ""
  /\ leftStep = 0
  /\ rightStep = 0
  /\ leftReleased = FALSE
  /\ rightReleased = FALSE
  /\ leftPayload = 0
  /\ rightPayload = 0
  /\ leftReleasePosition = 0
  /\ rightReleasePosition = 0

SynchronizedAction ==
  /\ leftStep' = leftStep + 1
  /\ rightStep' = rightStep + 1
  /\ leftReleased' = leftReleased \/ leftStep = 11
  /\ rightReleased' = rightReleased \/ rightStep = 11 + IF Config = "TimedRelease" /\ SecretRight = 1 THEN 1 ELSE 0
  /\ leftPayload' = 0
  /\ rightPayload' = 0
  /\ leftReleasePosition' = IF leftReleased' /\ ~leftReleased THEN leftStep + 1 ELSE leftReleasePosition
  /\ rightReleasePosition' = IF rightReleased' /\ ~rightReleased THEN rightStep + 1 ELSE rightReleasePosition

ProductNext == SynchronizedAction

CompleteObservation ==
  <<leftPayload, leftReleasePosition>> = <<rightPayload, rightReleasePosition>>

PayloadOnlyObservation == leftPayload = rightPayload

ProductSpec == ProductInit /\ [][ProductNext]_vars

====
