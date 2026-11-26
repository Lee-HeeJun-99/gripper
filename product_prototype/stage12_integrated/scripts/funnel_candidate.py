"""RevAD: finite curved lip entry, not deleting transverse capture.
Curvature envelope comes from declared60deg fixture, maximum PET/rail stock,
0.10mm normal running allowance. Candidate only; actual flexible loading unknown.
"""
import argparse,json,math,sys,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cut,box,rotate,export,volume,common,bounds,overlap,solid_count
from build_stage1 import compound
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    parent=ROOT/'cad/exports/revAC_pet_travel1/summary.json';old=json.loads(parent.read_text());files=dict(old['part_references']);parts={n:read(REPO/r['path']) for n,r in files.items()}
    R=88/(math.pi/3);cx=50.395-R;radius=R-.425-.100
    envelope=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(cx,-6.7,-95),gp_Dir(0,1,0)),radius,13.4).Shape()
    lip=box(48.98,-6.6,-95,.92,13.2,5);removal=cut(lip,envelope);front=cut(parts['F0_TERMINAL_FRONT'],removal)
    assert BRepCheck_Analyzer(front).IsValid() and solid_count(front)==1
    changes=[]
    for i in range(3):
        name=f'F{i}_TERMINAL_FRONT';shape=rotate(front,120*i);changes.append(dict(part_ID=name,removed_mm3=volume(parts[name])-volume(shape),STEP=None))
        export(shape,out/name);files[name]=ref(out/(name+'.step'));changes[-1].update(STEP=files[name],STL=ref(out/(name+'.stl')));parts[name]=shape
    checks=[]
    for theta in np.linspace(0,math.pi/3,31):
        for tp in (.28,.32):
            for tr in (.19,.21):
                # Corresponding physical stock / floating-front state, not mixed extrema.
                neutral=50.5-tr/2;d=tr/2+tp;frontfloat=.20-tr
                for z in np.linspace(-95,-90,51):
                    face=cx+math.sqrt(radius**2-(z+95)**2)+frontfloat
                    if theta==0:sheet=neutral-d
                    else:
                        rr=88/theta;sheet=neutral-rr+math.sqrt((rr-d)**2-(z+95)**2)
                    checks.append(sheet-face)
    boxes={n:bounds(s) for n,s in parts.items()};hits=[]
    for c in changes:
        name=c['part_ID']
        for n,s in parts.items():
            if n!=name and overlap(boxes[name],boxes[n]):
                v=common(parts[name],s)
                if abs(v)>1e-8:hits.append(dict(a=name,b=n,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='CANDIDATE_CURVATURE_APERTURE_PASS' if min(checks)>=.1-1e-10 and not hits else 'FAIL',revision=a.tag,parent=ref(parent),adopted=False,
        part_count=len(parts),changed=changes,part_references=files,assembly=ref(out/'ASSEMBLY.step'),nominal_end_gap_mm=1.8,
        funnel_profile=dict(center_X_mm=cx,center_Z_mm=-95,radius_mm=radius,Y_interval_mm=[-6.6,6.6],Z_interval_mm=[-95,-90],max_fixture_angle_deg=60),
        aperture_min_mm=min(checks),aperture_checks=len(checks),changed_vs_all_collisions=hits,
        lip_min_thickness_mm=cx+math.sqrt(radius**2-25)-48.98,
        producer=ref(out/'producer.py'),limitations=['Prescribed circular rail and stock envelope only, not free PET equilibrium','No physical strength, material, friction, fabrication or full Stage1 approval'],
        invalidated=['terminal lip machining/drawing/minimum section/strength','finite-channel contact','whole motion/tolerance/tool/service checks'],
        next='Solve PET against finite front/core/bottom surfaces; reconstruct actual BRep to reject missed contact')
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='part_references'},indent=2))
if __name__=='__main__':main()
