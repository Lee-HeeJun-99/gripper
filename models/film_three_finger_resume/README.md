# Persistent checkpoint transfer (experimental)

`ThreeFilmResumeODE` is a separate explicit persistent-contact entry point.
It reuses the original Lobatto equations,public mass reads,mapped commit and
whole-stage clearance. Original REST/window guards remain default virtual
policies in the original owners. No step-count spoofing is used.

V1 text checkpoint contains round-trip decimal doubles: accumulated absolute
time,dt,physical step index,runner-verified source/binary provenance token,
1953 reduced q/v,actual rigid quaternion xyzw,693 public nodal masses,36 public
rigid mass entries,three exact root index/weight arrays,and three accepted
finger/triangle/feature owners. Skin and rail coordinates share the reduced
blocks. The rotation chart resets to zero while the actual quaternion persists;
its sign is preserved,not silently canonicalized. Invalid norm is rejected.

Restore validates masses,mapping,selected rows,whole surface gap and tangent
velocity BEFORE physical writes. All11 public Context time/dt values are set
before AnimateBegin;actual mapped child positions/velocities are checked exactly.
Snapshots are exclusive files,one per accepted step. They represent the explicit
fixed independent compressive three-row branch,NOT arbitrary contact history,
release,friction,plasticity or multistep BDF state.

The Python exporter is narrowly restricted to Campaign1002's proven zero-spin
history. It refuses to invent a historical quaternion if any angular state is
nonzero. New actual checkpoints save the actual public quaternion directly.
The runner hashes source archive,binary,parent evidence,checkpoint and scene.
The C++ token comparison is NOT a standalone cryptographic file verifier;
use the guarded runners and their immutable manifest chain.

Legacy FilmRailTendon `previousLength/previousT/work` are private and NOT
restored. Their output has a new sampled-work origin and MUST NOT be spliced.
Stage power `-integral T dL` is independently evaluated from actual stage q/v,
with explicit physical-time origin and hash-bound preceding evidence. Root work
remains null. A signed residual is not physical heat or whole-energy certification.

Qualification:actual1014 four-step transfer and1015 serialization/retransfer,
1016 through10ms have q/v/time/used-stage rows EXACT to continuous1002 under
original strict1e-12 API gate. Field control/stored energies/geometry in1014
are exact too.1013 compile failure and1018 empty-header harness failure remain.
1019 read-only reassessment establishes five corrupted checkpoints reject before
any accepted step;invalid bwdInit currently throws/aborts rather than recovering.

Policy:4GiB/480s per child,forecast before each extension,exclusive Raw/build,
no SDK modifications,no remote push,no automatic background continuation.
