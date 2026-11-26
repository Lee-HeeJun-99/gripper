"""Independent candidate audit: correlated laminate thickness, not mixed states.
Old revAB_sliding_pet1 FAIL is immutable. No geometry changed by this audit.
"""
import argparse,json,math,sys
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage1_manufacturing/scripts'))
from incremental_stage1 import read,sha,common,volume,box,translate
from OCP.gp import gp_GTrsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'revised_cad/revAB_sliding_pet1';out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False)
    original=json.loads((source/'summary.json').read_text());checks=[]
    for x in original['modified']:
        path=source/x['STEP'];assert sha(path)==x['STEP_SHA256'];s=read(path);e=TopExp_Explorer(s,TopAbs_SOLID);n=0
        while e.More():n+=1;e.Next()
        mesh=trimesh.load(source/x['STL'],force='mesh');err=abs(mesh.volume/volume(s)-1)
        checks.append(dict(part=x['part'],single_solid=n==1,valid=BRepCheck_Analyzer(s).IsValid(),watertight=bool(mesh.is_watertight),positive=bool(mesh.is_volume),STL_volume_relative_error=err))
    front=read(source/'F0_TERMINAL_FRONT.step');s1=ROOT.parent/'stage1_manufacturing/cad/parts/revAA_mbd1'
    rails={n:read(s1/(n+'.step')) for n in ('F0_RAIL_L','F0_RAIL_R')};back=read(s1/'F0_TERMINAL_BACK.step')
    rows=[];advance=.265*math.pi/3+.15
    for tp in (.28,.32):
        for tr in (.19,.21):
            rear=50.5-tr;frontx=rear-tp
            envelope=box(frontx,-6.44,-94.4-advance,tp,12.88,4.4+advance)
            shifted_front=translate(front,.20-tr,0,0)
            bodies={'front':shifted_front,'back':back}
            for n,s in rails.items():
                t=gp_GTrsf();t.SetValue(1,1,tr/.20);t.SetValue(2,2,1);t.SetValue(3,3,1);t.SetValue(1,4,50.5*(1-tr/.20))
                bodies[n]=BRepBuilderAPI_GTransform(s,t,True).Shape()
            for n,s in bodies.items():
                v=common(envelope,s)
                rows.append(dict(PET_thickness_mm=tp,rail_thickness_mm=tr,PET_X_bounds_mm=[frontx,rear],front_float_mm=.2-tr,part=n,signed_common_mm3=v,status='PASS' if abs(v)<1e-8 else 'FAIL'))
    status='PASS' if all(x['single_solid'] and x['valid'] and x['watertight'] and x['positive'] and x['STL_volume_relative_error']<.01 for x in checks) and all(r['status']=='PASS' for r in rows) and not original['nominal_changed_vs_all_hits'] else 'FAIL'
    result=dict(status=status,scope='SIX CHANGED PARTS / NOMINAL304 CONTEXT + CORRELATED LOCAL END CLEARANCE ONLY',
        unchanged_geometry=True,geometry_source=str(source.relative_to(ROOT)),geometry_source_SHA256=sha(source/'summary.json'),
        checks=checks,correlated_cases=rows,source_SHA256=sha(Path(__file__)),
        diagnostic='Original worst envelope mixed PET rear50.31 from0.19 rail with NOMINAL0.20 rail front50.30; non-coexistent physical states. Here rear=50.5-tr, PET front=rear-tp and front clamp float=.20-tr for EACH case. No overlap threshold relaxed.',
        stage1_changed_gate_revalidation_complete=False,stage2_digital_release=False,
        further='Full candidate-specific unilateral layer/sliding-contact FEM, deformed motion, wire/tool/service geometry, finite radii, clamp stress and revised mass/inertia still required',
        command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/sliding_pet_audit.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='correlated_cases'},indent=2))
if __name__=='__main__':main()
