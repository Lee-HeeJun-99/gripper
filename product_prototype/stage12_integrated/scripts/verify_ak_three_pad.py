"""Independent volume/first-moment contact reconstruction and wrench checks."""
import json,sys,shutil,math
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import numpy as np

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_three_pad_verify2';out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/transmission/AK_three_pad2/summary.json';d=json.loads(source.read_text())
    inp=REPO/d['inputs']['path'];assert sha(inp)==d['inputs']['SHA256'];inputs=json.loads(inp.read_text())
    for r in [inputs['candidate'],inputs['producer'],*inputs['parts'].values(),*inputs['dependencies']]:assert sha(REPO/r['path'])==r['SHA256']
    palm=read(REPO/inputs['parts']['PALM']['path']);rows=[]
    for r in d['rows']:
        assert sha(REPO/r['pad']['path'])==r['pad']['SHA256']
        x,y,_=r['center_mm']
        for h in (.001,.002):
            shape=BRepAlgoAPI_Common(palm,cyl(3,(x,y,-12),h)).Shape()
            g=GProp_GProps();BRepGProp.VolumeProperties_s(shape,g)
            area=g.Mass()/h;c=g.CentreOfMass();target=r['centroid_mm']
            error=abs(area-r['area_mm2']);center_error=max(abs(c.X()-target[0]),abs(c.Y()-target[1])) if target else None
            rows.append(dict(pad=r['pad']['path'],slice_mm=h,area_mm2=area,area_error_mm2=error,centroid_error_mm=center_error,
                pass_check=bool(error<1e-5 and center_error is not None and center_error<1e-6)))
    # Cross-product virtual work; independent of hard-coded matrix row formula.
    W=np.array([np.r_[np.array([0.,0.,1.]),np.cross(r['centroid_mm'],[0,0,1])] for r in d['rows']]).T
    delta=np.array([.03,-.05,.07,.001,-.002,.003]);forces=np.array([.3,.7,.5])
    direct=sum(f*np.dot([0,0,1],delta[:3]+np.cross(delta[3:],r['centroid_mm'])) for f,r in zip(forces,d['rows']))
    work_error=abs(direct-np.dot(delta,W@forces))
    cases=[]
    for c in d['cases']:
        f=np.array(c['normal_reactions_N']);load=np.array(c['applied_wrench_N_Nmm']);res=max(abs(W@f+load))
        feasible=bool(res<1e-9 and min(f)>=-1e-10)
        cases.append(dict(label=c['label'],feasible=feasible,matches=feasible==c['feasible'],residual=float(res)))
    # A compression-only plane cannot oppose uplift or span Fx/Fy/Mz at any point.
    checks=dict(six_slices=len(rows)==6 and all(r['pass_check'] for r in rows),
        matrix_matches=bool(np.max(abs(W-np.array(d['normal_wrench_matrix'])))<1e-10),
        rank_three=bool(np.linalg.matrix_rank(W)==3),virtual_work=bool(work_error<1e-12),
        cases_match=all(r['matches'] for r in cases),center_supported=cases[0]['feasible'],
        four_load_cases_rejected=all(not r['feasible'] for r in cases[1:]),
        corrupt_area_rejected=all(abs(r['area_mm2']*1.01-d['rows'][i//2]['area_mm2'])>1e-5 for i,r in enumerate(rows)))
    ok=all(checks.values())
    dump(out/'summary.json',dict(status='INDEPENDENT_FINITE_PAD_VERIFICATION_PASS' if ok else 'FAIL',source=ref(source),producer=ref(out/'producer.py'),
        checks=checks,rows=rows,cases=cases,virtual_work_error_Nmm=work_error,
        scope='Actual contact footprint and rigid normal wrench basis; not full assembly equilibrium/strength/ground attachment',whole_system_release=False))
    print(json.dumps(dict(checks=checks,rows=rows,cases=cases),indent=2));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
