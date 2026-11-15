"""Fixed-denominator diagnostics; a local hold PASS is not convergence."""
import json
from beam_common import OUT,write_json
def main():
    target=OUT/'contact_convergence_audit.json'
    if target.exists():raise FileExistsError(target)
    names=['Tz_fixedinit','Tz_repeat','Tz_q16','Tz_q32','Tz_n21q32','Tz_halfdt','Tz_historyhalf','Tz_v2','Tz_n41q32_profiled']
    data={n:json.loads((OUT/'grasp'/n/'metrics.json').read_text()) for n in names}
    comparisons=[('repeat','Tz_fixedinit','Tz_repeat',1e-6),('quadrature_8_16','Tz_fixedinit','Tz_q16',.01),('quadrature_16_32','Tz_q16','Tz_q32',.01),('mesh_11_21','Tz_q32','Tz_n21q32',.01),('mesh_21_41','Tz_n21q32','Tz_n41q32_profiled',.01),('dt_half','Tz_fixedinit','Tz_halfdt',.001),('history_half','Tz_fixedinit','Tz_historyhalf',.01),('v1_v2_actual','Tz_fixedinit','Tz_v2',1e-12)]
    rows=[]
    for label,a,b,limit in comparisons:
        errors={k:abs(data[a][k]-data[b][k])/abs(data[b][k]) for k in ('hold_displacement_mm','hold_rotation_increment_rad')};rows.append(dict(name=label,coarse=a,fine=b,limit=limit,relative_errors=errors,status='PASS' if all(x<limit for x in errors.values()) else 'FAIL'))
    r=dict(status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL',comparisons=rows,metrics={n:{k:r.get(k) for k in ('status','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','bounded_hold_pass','recovery_pass')} for n,r in data.items()},source_caveat='prototype v1 binary frozen; some queued v1 records captured v2 working-tree snapshots. Compiled prototype manifest anchored to git4d19774 is authoritative. v2 compiled-source guard is strict; 100-state E/F/J equivalence and same-configuration actual v1-v2 are separate equivalence evidence, not mixed-study qualification.',full_grasp_gate=False,grasp_optimization_status='BLOCKED')
    write_json(target,r);print([(x['name'],x['status'],x['relative_errors']) for x in rows])
if __name__=='__main__':main()
