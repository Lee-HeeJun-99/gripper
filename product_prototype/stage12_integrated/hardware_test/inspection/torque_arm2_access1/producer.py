"""Actual pin removal and finite stock-socket key paths, OFF-BENCH subassembly.
Pin installation before bearings/support mounting; plugs removed before pin.
"""
import argparse,json,sys,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,fuse,cyl
from mechanisms_stage1 import hex_axis
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
def transform(s,T):return BRepBuilderAPI_Transform(s,T,True).Shape()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fixture',required=True);a=p.parse_args();out=ROOT/'hardware_test/inspection'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    path=ROOT/'hardware_test/fixtures'/a.fixture/'summary.json';d=json.loads(path.read_text());folder=path.parent;s={r['part']:read(folder/(r['part']+'.step')) for r in d['parts']};vertical=d.get('pin_axis')==[0,0,1];axis=np.array([0,0,1]) if vertical else np.array([1,0,0]);pins=[]
    for distance in range(25):
        v=common(translate(s['TORQUE_PIN'],*(axis*distance)),s['TORQUE_ARM']);pins.append(dict(distance_mm=distance,common_mm3=v))
    keys=[]
    if vertical:
        R=gp_Trsf();R.SetRotation(gp_Ax1(gp_Pnt(80,0,20),gp_Dir(0,1,0)),math.pi/2)
        for name,x,direction in [('PLUG_L',69,1),('PLUG_R',91,-1)]:
            point=(x,2.5,20);start=(x-direction*15,2.5,20)
            key=fuse(hex_axis(start,(direction,0,0),.9,15.8),hex_axis(start,(0,0,1),.9,25));key=transform(key,R)
            entry=R.Transformed(gp_Pnt(*point)) if False else gp_Pnt(*point).Transformed(R)
            for angle in range(0,361,30):
                T=gp_Trsf();T.SetRotation(gp_Ax1(entry,gp_Dir(0,0,1)),math.radians(angle))
                active=transform(s[name],T);tool=transform(key,T)
                hits=[]
                for n,part in s.items():
                    actual=active if n==name else part;v=common(tool,actual)
                    if abs(v)>1e-8:hits.append(dict(part=n,common_mm3=v))
                keys.append(dict(plug=name,angle_deg=angle,hits=hits))
    result=dict(status='PASS' if vertical and not any(abs(r['common_mm3'])>1e-8 for r in pins) and keys and not any(r['hits'] for r in keys) else 'FAIL',
        scope='OFF-BENCH ARM/PIN/PLUG ASSEMBLY, NOT FULL INSTALLED SUPPORT TOOL SWEEP',pin_extraction_cutset=['PLUG_L','PLUG_R'],pin_path=pins,key_paths=keys,
        fixture=ref(path),producer=ref(out/'producer.py'),physical_strength=False,tool_basis='Stage1same0.9AF finite L-bar; nominal stock sockets, not a claimed purchased-tool tolerance',
        assembly_order='Fit arm to shaft rotated90deg, insert Z pin, install both plugs on bench, then bearings/carriers; reverse bench removal before plug service',hardware_measured=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pin_collisions=[r for r in pins if abs(r['common_mm3'])>1e-8],key_collision_count=sum(bool(r['hits']) for r in keys)),indent=2))
if __name__=='__main__':main()
