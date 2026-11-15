"""Analysis-only restart after the recorded plotting syntax error; no reruns."""
from birth_common import OUT,write_json
from birth_finish import active
def main():
    if active():raise RuntimeError('wait for active physics before analysis finalization')
    write_json(OUT/'analysis_restart.json',dict(previous_status='FAIL',stage='post-physics module import',error="SyntaxError in birth_plot.py: conditional expression else20 missing space",fix='else 20; parse all birth tools and rerun ANALYSIS ONLY',physics_reexecuted=False,provenance='observed birth_finish.py terminal traceback; this is an incident record, not a fabricated raw stderr log'))
    import ast
    from birth_common import ROOT
    for path in(ROOT/'tools').glob('birth_*.py'):ast.parse(path.read_text(),filename=str(path))
    import birth_energy_audit,birth_memory,birth_assess,birth_plot
    for module in(birth_energy_audit,birth_memory,birth_assess,birth_plot):module.main()
    write_json(OUT/'finish_complete.json',dict(status='completed bounded execution and corrected analysis; not a full physics PASS'))
if __name__=='__main__':main()
