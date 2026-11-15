# Birth validation 06 COUPLED ENERGY

Status: BLOCKED full closure; partial engine journal implemented

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Optional in-engine journal records actual begin, force-method query, pre-contact Commit, post-contact Commit stages with Beam/FrameLayer energies, normal/tangent contact energies, actual kinetic energy, plastic dissipation and separate detachment inventory. Ideal tension cable T*L is only a virtual actuator potential; endpoint work -T_begin DeltaL is logged separately.

Pressure parameter work, Rayleigh stiffness dissipation and global closure remain null, NOT zero. FrameLayer may commit before contact pre-commit. Recorder/init force queries are distinguishable calls but are NOT guaranteed Solver stages. No direct Solver transaction hook exists yet. Thus this is a synchronized CONTACT-owner journal, not an all-owner global journal. Unexplained residual is never defined to be numerical heat. See energy_audit.json when actually generated; missing outputs mean NOT RUN, not PASS.

Actual24s contact-owner journal:194401rows,48000pre/post transactions, all known fields finite; contact normal+tangent split discrepancy<=1.23e-20. Journal ON/OFF state SHA256 both `330807bfd9237f66866620f400b55470dbf662421e6a5c0aa1e88a0bd00d1bc3`. Unknown columns remain null.
