"""Finite common-patch normal-pressure witness, not a loaded contact solution."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,translate,bounds
from ak_root_clamp_contact import faces,props
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def intersect(a,b):
    op=BRepAlgoAPI_Common(a,b);op.Build();assert op.IsDone();return op.Shape()
def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/AK_root_pressure1';out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/finger/AK_root_clamp_contact2/summary.json';d=json.loads(src.read_text())
    candidate=json.loads((REPO/d['candidate']['path']).read_text())
    for r in [d['candidate'],*candidate['part_references'].values()]:assert sha(REPO/r['path'])==r['SHA256']
    dump(out/'inputs.json',dict(source=ref(src),producer=ref(out/'producer.py'),parts=d['inputs'],dependencies=[ref(ROOT/'scripts/ak_root_clamp_contact.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],plan='Fixed z4..6mm band, common projected actual contacts on each rail; unit compression only. Area>1e-6, centroid z5 within1e-6mm, wrench residual<1e-6Nmm. No material or preload inference.'))
    ss={n:read(REPO/r['path']) for n,r in d['inputs'].items() if 'BOLT' not in n}
    patches=[]
    for side in ['L','R']:
        rail='F0_RAIL_'+side
        edges=[('F0_ROOT_FRONT','F0_SKIN'),('F0_SKIN',rail),(rail,'F0_ROOT_BACK')]
        shapes=[]
        for a,b in edges:
            hits=[]
            for fa,xa in faces(ss[a]):
                for fb,xb in faces(ss[b]):
                    if abs(xa-xb)<1e-9:
                        q=intersect(fa,fb)
                        if props(q)[0]>1e-8:
                            q=intersect(q,box(30,-30,4,40,60,2))
                            if props(q)[0]>1e-8:hits.append(translate(q,-xa,0,0))
            assert len(hits)==1,(side,a,b,len(hits))
            shapes.append(hits[0])
        q=intersect(intersect(shapes[0],shapes[1]),shapes[2]);area,c=props(q)
        from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
        w=STEPControl_Writer();w.Transfer(q,STEPControl_AsIs);w.Write(str(out/f'COMMON_{side}.step'))
        patches.append(dict(side=side,area_mm2=area,centroid_mm=c,bounds_mm=bounds(q),shape=ref(out/f'COMMON_{side}.step'),normal_force_N=.5,pressure_MPa_per_unit_total_N=.5/area))
    cy=sum(.5*p['centroid_mm'][1] for p in patches);cz=sum(.5*p['centroid_mm'][2] for p in patches)
    bolt_y=sum(b['axis_yz_mm'][0] for b in d['bolts'])/2;bolt_z=sum(b['axis_yz_mm'][1] for b in d['bolts'])/2
    checks=dict(positive_finite_patches=all(p['area_mm2']>1e-6 for p in patches),unit_force=True,normal_moment_balance=max(abs(cy-bolt_y),abs(cz-bolt_z))<1e-6)
    dump(out/'summary.json',dict(status='FINITE_PRESSURE_WITNESS_PASS' if all(checks.values()) else 'FINITE_PRESSURE_WITNESS_FAIL',inputs=ref(out/'inputs.json'),patches=patches,checks=checks,unit_resultant_yz_mm=[cy,cz],bolt_resultant_yz_mm=[bolt_y,bolt_z],old_uniform_residual_Nmm_per_N=d['uniform_front_pressure_moment_residual_Nmm_per_N'],whole_system_release=False,physical_preload_N=None,limitations=['Necessary rigid-body normal equilibrium witness only; pressure not solved from bolt/plate deformation','In-plane bolt-to-patch load spreading, local bending/stress, tolerances, friction and full Finger remain unqualified','Equal hypothetical bolt forces; actual preload and capacities unknown; candidate/adopted CAD unchanged']))
    print(json.dumps(dict(checks=checks,patches=patches)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
