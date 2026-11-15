"""Preserve original blocked decision; assess actual one-off quarter result."""
import json
import xml.etree.ElementTree as ET
from curve_common import OUT, sha, write_json
from birth_assess import same_physics, observables
from history_assess import comparison


def main():
    target=OUT/'quarterdt_actual_assessment.json'
    if target.exists():raise ValueError('refuse overwritten quarter evidence')
    names=('n21','halfdt','quarterdt_exception')
    records={n:json.loads((OUT/'grasp'/n/'metrics.json').read_text())for n in names}
    checks={}
    for a,b in(('n21','halfdt'),('halfdt','quarterdt_exception'),('n21','quarterdt_exception')):
        u,v=records[a],records[b];same_physics(u,v)
        if u['identity']['curved']!=v['identity']['curved']or u['identity']['inherited']['inherited']['beam']['plugin_sha256']!=v['identity']['inherited']['inherited']['beam']['plugin_sha256']:raise ValueError('compiled runtime differs')
        for k in('nodes','history','layout_policy','mass_quadrature'):
            if u['config'].get(k)!=v['config'].get(k):raise ValueError('different experimental definition '+k)
        # Earlier frozen configs predate the descriptive solver_template key.
        # Verify actual input scenes instead of inferring identity from a label.
        solver=[]
        for n in(a,b):
            e=ET.parse(OUT/'grasp'/n/'scene.scn').getroot().find('.//EigenSparseLU')
            if e is None:raise ValueError('actual EigenSparseLU missing')
            solver.append(e.get('template','CompressedRowSparseMatrixMat3x3d'))
        if solver[0]!=solver[1]:raise ValueError('actual solver template differs')
        r=comparison(u,v,.001);r['motion_only_status']=r['status']
        x,y=observables(OUT/'grasp'/a),observables(OUT/'grasp'/b)
        d=abs(x['friction_dissipation']-y['friction_dissipation'])/abs(y['friction_dissipation'])
        r.update(loss_relative=d,loss_absolute=abs(x['friction_dissipation']-y['friction_dissipation']),loss_status='PASS'if d<=.001 else'FAIL',underlying_physical_checks={n:records[n]['checks']for n in(a,b)})
        r['status']='PASS'if r['motion_only_status']=='PASS'and r['loss_status']=='PASS'and u.get('bounded_hold_pass')and v.get('bounded_hold_pass')else'FAIL'
        checks[a+'_'+b]=r
    write_json(target,dict(status='FAIL',checks=checks,actual_quarter_process=records['quarterdt_exception']['process'],original_900s_blocked_decision_preserved=True,grasp_optimization='BLOCKED',scope='Numerical differences remain visible but underlying global moment FAIL forbids time qualification;18s is not24s recovery'))
    print({n:(r['status'],r['motion_only_status'],r['loss_status'],r['loss_relative'])for n,r in checks.items()})


if __name__=='__main__':main()
