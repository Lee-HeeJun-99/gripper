"""Five prescribed Finger poses: finite wires vs actual rigid hardware.

No elastic PET/Rail trajectory is invented. Those three elastic parts/sector
are explicitly OUTSIDE this rigid-hardware screen, not disabled in a simulator.
"""
import argparse,json,math,shutil,sys,itertools
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump,sha
from drive_system_layout import wire
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,rotate,bounds,overlap,common,export,volume,solid_count
import wire_motion as wm
from mechanism_motion import rot,tip
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer

def transform(s,M):
    tr=gp_Trsf();tr.SetValues(*[float(v) for v in M[:3,:].ravel()]);return BRepBuilderAPI_Transform(s,tr,True).Shape()

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(source.read_text());shapes={}
    for n,r in d['part_references'].items():
        p=REPO/r['path'];assert sha(p)==r['SHA256'];shapes[n]=read(p)
    rows=[];hits=[];compares=0
    for deg in (0,15,30,45,60):
        cable,g=wire(deg);assert BRepCheck_Analyzer(cable).IsValid() and solid_count(cable)==1
        export(cable,out/f'F0_WIRE_{deg}')
        theta=math.radians(deg);T=tip(theta);q=wm.path(deg);b0=wm.path(0)['beta'];S=rot(q['beta']-theta-b0,point=q['P'])@T
        R=rot(g['rotor_angle_rad'],point=[110,0,20]);targets={}
        for n,s in shapes.items():
            if n.endswith(('SKIN','RAIL_L','RAIL_R','TENDON_WIRE')):continue
            if not n.startswith(('F0_','F1_','F2_')):targets[n]=s;continue
            sector=int(n[1]);suffix=n[3:];local=rotate(s,-120*sector)
            if suffix.startswith(('SWIVEL_LOWER','SWIVEL_UPPER','SWIVEL_BOLT','SWIVEL_NUT','TIP_FACTORY_NIPPLE')):local=transform(local,S)
            elif 'TERMINAL' in suffix or suffix.startswith(('SWIVEL_AXLE','SWIVEL_SLEEVE','SWIVEL_SPACER_')):local=transform(local,T)
            elif (suffix.startswith('DRUM') or suffix.startswith('CLUTCH')) and suffix not in ('CLUTCH_BEARING','CLUTCH_INNER_CLIP') and not suffix.startswith('CLUTCH_GROUND_'):local=transform(local,R)
            targets[n]=rotate(local,120*sector)
        bb={n:bounds(s) for n,s in targets.items()};wires={f'F{i}_WIRE':rotate(cable,120*i) for i in range(3)}
        for n,s in wires.items():
            b=bounds(s)
            for m,t in targets.items():
                if overlap(b,bb[m]):
                    compares+=1;v=common(s,t)
                    if abs(v)>1e-8:hits.append(dict(angle_deg=deg,a=n,b=m,common_mm3=v))
        for (n,s),(m,t) in itertools.combinations(wires.items(),2):
            v=common(s,t)
            if abs(v)>1e-8:hits.append(dict(angle_deg=deg,a=n,b=m,common_mm3=v))
        rows.append(dict(angle_deg=deg,wire_volume_mm3=volume(cable),length_mm=g['free_length_mm'],rotor_angle_rad=g['rotor_angle_rad'],wire=ref(out/f'F0_WIRE_{deg}.step')))
    result=dict(status='WIRE_RIGID_HARDWARE_SCREEN_PASS' if not hits else 'WIRE_RIGID_HARDWARE_SCREEN_FAIL',scope='Actual nominal0.5mm finite wires against actual rigid hardware at five prescribed0..60deg poses; wire-wire included. Not whole Finger or continuous collision/dynamics qualification.',candidate=ref(source),producer=ref(out/'producer.py'),wire_implementation=ref(ROOT/'scripts/drive_system_layout.py'),mechanism_implementation=ref(S1/'scripts/mechanism_motion.py'),rows=rows,hits=hits,comparisons=compares,
        exclusions=['Independent PET/Rail deformed shape unresolved; no common-curvature envelope substituted','No maximum-stock diameter/length/tolerance screen','No actual dynamic wire sliding, friction or tension','No proof of powered actuation or whole Stage1 release'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],comparisons=compares,hits=hits),indent=2))
if __name__=='__main__':main()
