# Separate stationary-object closing experiment

This is a NEW initial-value problem, not a modified incoming-impact checkpoint.
Three rest FilmLateralTendon fingers, one stationary free100g sphere, zero
gravity/external load; same100mm/50mm layout, R30 sphere/buffer30.01,
extra initial body Z clearance .0001mm, same C2 .0001N/rail rise10ms.
Material, density assumptions and thickness-clearance limitations are unchanged.

`LateralRestClosingODE` checks actual public rest q/v/quaternion, body freedom,
root map/mass through inherited public API, and exact accumulated clocks.
It uses the existing free implicit midpoint and numerical dense-surface path
CCD, refusing to commit a first contact. It is NOT a sustained-contact/grasp
owner. Its checkpoint schema is REGRIP_LATERAL_REST_FREE_V1, distinct from
the released incoming-object history; the two histories must never be spliced.

1538/1540 actual1.6ms,1541 actual10ms: no contact, control error0, q/v exact
to the independent public-mass reference.1539 strict API velocity error
3.06954e-12mm/s FAIL is preserved.1543 shows all actual model sources,
binary and physical CSV bytes unchanged: binding the reference to actual
public masses makes the API error0. No tolerance or physical-state adjustment.
1535 reference API compile failure also remains archived.

No contact by the first tension peak does not prove eventual failure;
conversely incoming-body contact does not prove tendon capture from rest.
Longer stationary-object contact/release, error-controlled temporal convergence,
friction, thickness and lift remain unqualified. Resume beyond10ms requires
a separately validated typed owner, not the incoming-object FREE schema.
`film_lateral_rest_resume` provides that separate owner;1545 qualifies its
first actual10..10.2ms step with exact API comparison. Longer intervals
still require their own tests and may reject a new contact birth.

`tools/film_lateral_rest_closing.py --reuse QUALIFIED_CASE` explicitly uses
the frozen provider's complete compiled source archive and validates ALL
source/binary hashes. It does not silently compile current working-tree changes.
