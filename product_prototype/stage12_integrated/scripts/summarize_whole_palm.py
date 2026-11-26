"""Record one bounded actual AK whole-Palm conditional-support experiment."""
import json,shutil
from baseline_registry import ROOT,REPO,ref,dump
from integrated_release_gate import audit

def main():
    out=ROOT/'validation/transmission/AK_whole_palm_cycle1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    rows=[]
    for tag in ('AK_whole_palm_h8_3','AK_whole_palm_h6_1','AK_whole_palm_h4_1'):
        p=ROOT/'validation/transmission'/tag/'summary.json';d=json.loads(p.read_text());rows.append(dict(result=ref(p),h_mm=d['h_mm'],compliance_m_N=d['compliance_m_N'],peak_unsmoothed_vm_Pa=d['peak_unsmoothed_vm_Pa'],minimum_quality=d['min_quality'],checks=d['checks'],elapsed_s=d['elapsed_s'],elements=d['elements']))
    convergence=[dict(pair=[a['h_mm'],b['h_mm']],compliance_fraction=abs(a['compliance_m_N']/b['compliance_m_N']-1),peak_stress_fraction=abs(a['peak_unsmoothed_vm_Pa']/b['peak_unsmoothed_vm_Pa']-1)) for a,b in zip(rows,rows[1:])]
    v=ROOT/'validation/transmission/AK_whole_palm_verify1/summary.json'
    dump(out/'summary.json',dict(status='FAIL',scope='Actual whole AK Palm conditional central clamp and unit outer-mount loading; NOT assembled system or strength qualification',starting_HEAD='c1cd83ef0cabad1703a1c56f02c932f5287db3d2',rows=rows,convergence=convergence,response_limit_fraction=.01,verification=ref(v),producer=ref(out/'producer.py'),failures=['First face-selection assertion exit1 retained in h8.log and AK_whole_palm_h8_1','Second single-face assertion exit1 retained in h8_2.log and AK_whole_palm_h8_2; actual washer spans six STEP fragments','Mesh-quality threshold .01 is unchanged; failed states retained'],physical_assumptions=['Actual entire AK Palm STEP and actual x127/y-1mm hole','Hypothetical fully fixed underside central annulus r20..30mm, NOT identified assembly support','Uniform 1N downward traction at r1.7..4mm outer mounting washer; not solved bolt preload','E70GPa nu.33 assumed linear isotropic material'],whole_system_release=False,save_status='PENDING_SUPERVISOR_LOCAL_SAVE'))
    release=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()));release['producer']=ref(out/'producer.py');dump(out/'release_summary.json',release)
    execution=ROOT/'validation/transmission/AK_palm_execution1'
    dump(execution/'summary.json',dict(status='COMPLETED_WITH_FAILURES',memory_limit_KiB=4194304,timeout_seconds_per_child=420,SOFA_executed=False,children=[dict(log=ref(execution/n),exit_code=c) for n,c in [('h8.log',1),('h8_2.log',1),('h8_3.log',0),('h6.log',0),('h4.log',0),('verify.log',0)]],acceptance='Actual metrics in cycle summary; exit0 is not PASS',live_analysis_children=0))
    print(json.dumps(dict(rows=rows,convergence=convergence,release=release['status']),indent=2))
if __name__=='__main__':main()
