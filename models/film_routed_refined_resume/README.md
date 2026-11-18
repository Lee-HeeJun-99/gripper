# Explicit routed one-step refinement

Separate module,compiled only against verified routed1278 headers. It restores
an actual V1 physical checkpoint at its recorded accumulated time/used dt,then
sets every public Context's NEXT dt to100us BEFORE animation. No q/v/rotation,
mass,root mapping,contact row,force,tolerance or step count is overwritten.
Output HALF_V1 records actual used100us and accepted-step count. This is NOT
an error-controlled adaptive method or a fix of old200us FAIL records.

The runner binds the new executable and old immutable checkpoint by a new
provenance token;only the token in a COPY changes,not physical state. Legacy
Field sampled-work remains unrestored/excluded. General release/recontact,
friction,selfcollision,physical thickness and whole time/energy remain blocked.
