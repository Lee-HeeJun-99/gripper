"""Independent volume/first-moment check of actual planar root contacts."""
import json,sys,shutil,copy
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,translate
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def measure(a,b,dx):
    op=BRepAlgoAPI_Common(translate(a,dx,0,0),b);op.Build();assert op.IsDone()
    p=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),p);c=p.CentreOfMass()
    return dict(dx_mm=dx,volume_mm3=p.Mass(),area_mm2=p.Mass()/dx,centroid_yz_mm=[c.Y(),c.Z()])
def check(contact,m):
    return abs(contact['area_mm2']-m['area_mm2'])<1e-6 and max(abs(contact['centroid_mm'][j+1]-m['centroid_yz_mm'][j]) for j in range(2))<1e-7

def main():
    assert not (ROOT/'runtime/STOP').exists()
    src=ROOT/'validation/finger/AK_root_clamp_contact2/summary.json';d=json.loads(src.read_text())
    out=ROOT/'validation/finger/AK_root_clamp_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    assert sha(REPO/d['producer']['path'])==d['producer']['SHA256']
    for r in d['inputs'].values():assert sha(REPO/r['path'])==r['SHA256']
    ss={n:read(REPO/r['path']) for n,r in d['inputs'].items()}
    for n in ['F0_SKIN','F0_RAIL_L','F0_RAIL_R']:ss[n]=BRepAlgoAPI_Common(ss[n],box(30,-30,-7,40,60,17)).Shape()
    rows=[]
    for c in d['contacts']:
        m=[measure(ss[c['a']],ss[c['b']],x) for x in [.001,.002]]
        rows.append(dict(a=c['a'],b=c['b'],measurements=m,area_and_first_moment_pass=all(check(c,v) for v in m)))
    f=d['contacts'][0];perturbed=copy.deepcopy(f);perturbed['area_mm2']*=1.01
    control=not check(perturbed,rows[0]['measurements'][0])
    moment=5-rows[0]['measurements'][0]['centroid_yz_mm'][1]
    moment_ok=abs(moment-d['uniform_front_pressure_moment_residual_Nmm_per_N'])<1e-7 and abs(moment)>1
    checks=dict(all_five_interfaces_verified=len(rows)==5 and all(r['area_and_first_moment_pass'] for r in rows),one_percent_area_corruption_rejected=control,uniform_pressure_moment_verified=moment_ok,no_physical_preload_invented=all(d[k] is None for k in ['normal_preload_N','friction_coefficients','axial_capacity_N']))
    result=dict(status='CONTACT_AREA_FIRST_MOMENT_VERIFIED' if all(checks.values()) else 'VERIFICATION_FAIL',source=ref(src),producer=ref(out/'producer.py'),rows=rows,checks=checks,uniform_front_pressure_moment_residual_Nmm_per_N=moment,whole_system_release=False,scope='Independent thin-overlap volume and volume centroid, not repeated face-face area; nominal sector0 root geometry only',limitations=['Neither method determines elasticity, contact pressure distribution, friction or bolt tension','No whole Finger, preload or safe force PASS'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
