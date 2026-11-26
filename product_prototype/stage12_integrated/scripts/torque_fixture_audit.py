"""Independent actual fixture mesh/integral/shaft-interface check."""
import argparse,json,sys,shutil
from pathlib import Path
import numpy as np
import trimesh
from baseline_registry import ROOT,S1,S2,REPO,ref,dump
sys.path.insert(0,str(S2/'scripts'));sys.path.insert(0,str(S1/'scripts'))
from extract_geometry import load,properties
from incremental_stage1 import common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'hardware_test/inspection'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'hardware_test/fixtures/torque_arm1/summary.json';d=json.loads(source.read_text());shapes={};checks=[]
    for r in d['parts']:
        s=load(REPO/r['STEP']['path']);v,c,j=properties(s);mesh=trimesh.load(REPO/r['STL']['path'],force='mesh');err=abs(mesh.volume*1e-9/v-1)
        shapes[r['part']]=s;checks.append(dict(part=r['part'],watertight=bool(mesh.is_watertight),positive=bool(mesh.is_volume),volume_relative=err,centroid_m=c.tolist()))
    arm=next(r for r in checks if r['part']=='TORQUE_ARM');balanced=abs(arm['centroid_m'][0]-.08)<1e-9
    # Explicit bench assembly: actual shaft, both bearing/pedestal supports and
    # Palm only. Not the complete gripper with its Idler/Drum still installed.
    names=['PALM','F0_SHAFT','F0_BEARING_L','F0_BEARING_R','F0_PEDESTAL_L','F0_PEDESTAL_R']
    supports={n:load(S1/'cad/parts/revAA_mbd1'/(n+'.step')) for n in names};hits=[]
    for angle in np.linspace(-5,5,11):
        T=gp_Trsf();T.SetRotation(gp_Ax1(gp_Pnt(80,0,20),gp_Dir(0,1,0)),float(np.radians(angle)))
        for name,s in shapes.items():
            q=BRepBuilderAPI_Transform(s,T,True).Shape()
            for n,body in supports.items():
                # Shaft rotates with the pin/arm. Its matching pin hole must be
                # transported too, not falsely tested against an immobile hole.
                actual=BRepBuilderAPI_Transform(body,T,True).Shape() if n=='F0_SHAFT' else body
                v=common(q,actual)
                if abs(v)>1e-8:hits.append(dict(angle_deg=float(angle),a=name,b=n,common_mm3=v))
    result=dict(status='PASS' if balanced and not hits and all(r['watertight'] and r['positive'] and r['volume_relative']<.01 for r in checks) else 'FAIL',scope='ACTUAL BENCH FIXTURE / DECLARED SUPPORT SUBASSEMBLY,11SAMPLED +/-5deg POSES ONLY',
        source=ref(source),checks=checks,nominal_counterbalance_CoM_verified=balanced,hits=hits,supports={n:ref(S1/'cad/parts/revAA_mbd1'/(n+'.step')) for n in names},
        producer=ref(out/'producer.py'),load_proof=False,hardware_measured=False,remaining='Rated bench attachments/stops/sensor link, pin/contact/thread/local stress, physical calibration and safe load approval')
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
