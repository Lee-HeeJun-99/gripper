"""Actual root contact areas + independent axial friction-network contract.

No actual friction or bolt preload is supplied. Solve normalized capacity
S=mu*N for a common-unknown-mu scenario. Distinct materials require separate
edge coefficients before use. Root bending/transverse compliance NOT covered.
"""
import argparse,json,itertools,shutil,sys
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

EDGES=[('G','P',1.),('P','L',.5),('P','R',.5),('G','L',.5),('G','R',.5)]
def solve(force):
    B=np.zeros((3,5));labels=['P','L','R']
    for j,(u,v,c) in enumerate(EDGES):
        if u in labels:B[labels.index(u),j]=-1
        if v in labels:B[labels.index(v),j]=1
    A=[];b=[]
    for j,(u,v,c) in enumerate(EDGES):
        for sign in (-1,1):
            row=np.zeros(6);row[0]=-c;row[j+1]=sign;A.append(row);b.append(0.)
    A=np.array(A);r=linprog([1,0,0,0,0,0],A_ub=A,b_ub=b,A_eq=np.c_[np.zeros(3),B],b_eq=-np.array(force),bounds=[(0,None)]+[(None,None)]*5,method='highs')
    assert r.success
    cuts=[]
    for n in (1,2,3):
        for subset in itertools.combinations(labels,n):
            cap=sum(c for u,v,c in EDGES if (u in subset)!=(v in subset))
            demand=abs(sum(force[labels.index(k)] for k in subset));cuts.append(dict(subset=subset,bound=demand/cap))
    exact=max(x['bound'] for x in cuts);res=B@r.x[1:]+force;slack=-A@r.x
    dual=float(np.dot(np.array(force)*-1,r.eqlin.marginals))
    ok=abs(exact-r.x[0])<1e-9 and np.max(abs(res))<1e-8 and min(slack)>-1e-10 and abs(dual-r.x[0])<1e-8
    return dict(layer_axial_forces_N=list(force),minimum_mu_times_normal_preload_N=float(r.x[0]),flows_N=r.x[1:].tolist(),cut_bound_N=exact,cuts=cuts,force_residual_N=res.tolist(),friction_min_slack_N=float(min(slack)),dual_gap_N=abs(dual-r.x[0]),status='PASS' if ok else 'FAIL')

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAD_funnel1/summary.json';d=json.loads(src.read_text());areas=[]
    for n,t in [('F0_SKIN',.3),('F0_RAIL_L',.2),('F0_RAIL_R',.2)]:
        r=d['part_references'][n];path=REPO/r['path'];assert sha(path)==r['SHA256']
        s=read(path);piece=BRepAlgoAPI_Common(s,box(46,-21,-7,18,42,17)).Shape();area=volume(piece)/t
        assert area>0;areas.append(dict(part=n,STEP=r,root_Z_mm=[-7,10],thickness_mm=t,projected_root_area_mm2=area))
    forces=[(1.,0.,0.),(0.,1.,0.),(0.,0.,1.),(0.,1.,1.),(-39.1408,19.5704,19.5704)]
    rows=[solve(f) for f in forces]
    for row in rows:
        S=row['minimum_mu_times_normal_preload_N']
        row['normal_preload_requirement']='N >= '+str(S)+' / measured_lower_bound_mu'
        row['conditional_mu_times_mean_contact_pressure_Pa']=[S/(areas[0]['projected_root_area_mm2']*1e-6),S/(2*areas[1]['projected_root_area_mm2']*1e-6),S/(2*areas[2]['projected_root_area_mm2']*1e-6)]
    result=dict(status='CONDITIONAL_ROOT_RETENTION_CONTRACT_PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',scope='Actual root area inventory and axial-only normalized contact-capacity equilibrium, not assembled strength or measured preload',source=ref(src),producer=ref(out/'producer.py'),areas=areas,edges=EDGES,rows=rows,
        assumptions=['One common friction coefficient, NOT an actual material value','Equal normal load on each Rail, total normal clamp load N','Finite uniform contact area approximation, no pressure redistribution or root compliance','Unit-force influence cases and prior conditional self-stress reference only, not RevAD/AG actual forces'],
        design_conclusion='Net axial load near zero does not remove separate layer retention demand. Need actual preload/friction or positive mechanical root capture.',
        excluded=['actual friction and bolt preload','large-deformation actual Finger loads','root bending/contact separation','PET compression/creep and Rail local bearing','manufacturing strength, hardware or powered operation'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],areas=areas,requirements=[dict(force=r['layer_axial_forces_N'],muN=r['minimum_mu_times_normal_preload_N']) for r in rows]),indent=2))
if __name__=='__main__':main()
