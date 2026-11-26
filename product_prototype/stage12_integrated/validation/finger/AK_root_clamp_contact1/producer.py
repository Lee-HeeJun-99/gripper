"""Actual AK root normal-contact/preload geometry; no inferred physical preload."""
import json,sys,shutil
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def props(s):
    p=GProp_GProps();BRepGProp.SurfaceProperties_s(s,p);c=p.CentreOfMass()
    return p.Mass(),[c.X(),c.Y(),c.Z()]
def faces(s):
    e=TopExp_Explorer(s,TopAbs_FACE);out=[]
    while e.More():
        f=TopoDS.Face_s(e.Current());a=BRepAdaptor_Surface(f)
        if a.GetType()==GeomAbs_Plane and abs(abs(a.Plane().Axis().Direction().X())-1)<1e-10:
            out.append((f,a.Plane().Location().X()))
        e.Next()
    return out

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/AK_root_clamp_contact1';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(src.read_text());rr=d['part_references'];assert len(rr)==235
    for r in rr.values():assert sha(REPO/r['path'])==r['SHA256']
    names=['F0_ROOT_FRONT','F0_SKIN','F0_RAIL_L','F0_RAIL_R','F0_ROOT_BACK']
    ss={n:read(REPO/rr[n]['path']) for n in names};ff={n:faces(s) for n,s in ss.items()}
    contacts=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            patches=[]
            for fa,xa in ff[a]:
                for fb,xb in ff[b]:
                    if abs(xa-xb)>1e-9:continue
                    op=BRepAlgoAPI_Common(fa,fb);op.Build();assert op.IsDone();area,c=props(op.Shape())
                    if area>1e-8:patches.append(dict(area_mm2=area,centroid_mm=c,bounds_mm=bounds(op.Shape())))
            if patches:
                area=sum(p['area_mm2'] for p in patches);centroid=[sum(p['area_mm2']*p['centroid_mm'][j] for p in patches)/area for j in range(3)]
                contacts.append(dict(a=a,b=b,patches=patches,area_mm2=area,centroid_mm=centroid,mean_pressure_MPa_per_N=1/area))
    # Finite closure is an interference witness, never an elastic compression solve.
    closure=[]
    for a,b in [('F0_ROOT_FRONT','F0_SKIN'),('F0_RAIL_L','F0_ROOT_BACK'),('F0_RAIL_R','F0_ROOT_BACK'),('F0_ROOT_FRONT','F0_ROOT_BACK')]:
        states=[dict(dx_mm=x,overlap_mm3=common(translate(ss[a],x,0,0),ss[b])) for x in [0,.001,.002]]
        closure.append(dict(a=a,b=b,states=states))
    bolts=[]
    for n in ['F0_ROOT_BOLT_-16','F0_ROOT_BOLT_16']:
        b=bounds(read(REPO/rr[n]['path']));bolts.append(dict(part=n,bounds_mm=b,axis_yz_mm=[(b[1]+b[4])/2,(b[2]+b[5])/2]))
    front=next(c for c in contacts if c['a']=='F0_ROOT_FRONT' and c['b']=='F0_SKIN')
    bolt_z=sum(b['axis_yz_mm'][1] for b in bolts)/2
    residual=bolt_z-front['centroid_mm'][2]
    checks=dict(five_contact_edges=len(contacts)==5,nominal_zero_overlap=all(abs(r['states'][0]['overlap_mm3'])<1e-8 for r in closure),closure_hits_material=all(r['states'][1]['overlap_mm3']>1e-8 for r in closure[:3]),no_direct_clamp_bypass_at_2um=closure[-1]['states'][-1]['overlap_mm3']<1e-8)
    result=dict(status='ACTUAL_ROOT_NORMAL_PATH_IDENTIFIED_PRELOAD_UNQUALIFIED' if all(checks.values()) else 'CONTACT_ANALYSIS_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs={n:rr[n] for n in names+[b['part'] for b in bolts]},contacts=contacts,closure_witnesses=closure,bolts=bolts,checks=checks,
        uniform_front_pressure_moment_residual_Nmm_per_N=residual,
        normal_preload_N=None,friction_coefficients=None,axial_capacity_N=None,whole_system_release=False,
        interpretation='Contact graph FRONT->SKIN->two RAILS->BACK. Front full-area uniform pressure with equal bolt preload leaves a nonzero y moment; pressure distribution/plate bending must be solved, not replaced by fixed PET/Rail roots.',
        conditional_bound='If external total normal preload P is established on each outer clamp face, axial force magnitude cannot exceed (mu_FRONT_SKIN + mu_RAIL_BACK_max)*P by Coulomb force balance. This is only a necessary upper bound; internal transfer, moments, bending, slip and material limits can reduce it.',
        limitations=['Planar nominal CAD contacts, not tolerance or loaded contact qualification','Unit-pressure coefficients do not establish actual pressure or bolt preload','Rigid translation overlaps are not deformations or a stiffness estimate','All 235 source hashes checked; only sector0 contact path analyzed','No SOFA, full Finger solve, strength, safe load or system release'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,contacts=[(c['a'],c['b'],c['area_mm2'],c['centroid_mm']) for c in contacts],moment_per_N=residual)))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
