"""Locate stored finite-PET overlap in actual terminal coordinates; no new solve."""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,S2,ref,dump
from deformed_channel_screen import pet
from incremental_stage1 import read,common,volume,bounds,box
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Trsf
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/finger/finite_pet_AC1/summary.json';d=json.loads(source.read_text());records=[]
    front=read(S2/'revised_cad/revAB_sliding_pet1/F0_TERMINAL_FRONT.step');old=read(S1/'cad/parts/revAA_mbd1/F0_TERMINAL_FRONT.step')
    for row in d['rows']:
        if row['n']!=32:continue
        t=math.radians(row['fixture_angle_deg']);R=.088/t;c,s=math.cos(t),math.sin(t);M=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        end=np.array([50.4-R*(1-c)*1000,0,-7-R*s*1000]);shift=end-M@np.array([50.4,0,-95.]);tr=gp_Trsf();tr.SetValues(*[float(v) for i in range(3) for v in (*M[i],shift[i])]);tr.Invert()
        shape=BRepBuilderAPI_Transform(pet(row['state_angles_rad'],d['PET_free_length_m'],4),tr,True).Shape()
        intersection=BRepAlgoAPI_Common(shape,front).Shape()
        lip=box(48.98,-6.6,-95,.92,13.2,5)
        records.append(dict(angle_deg=row['fixture_angle_deg'],intersection_local_bounds_mm=bounds(intersection),total_common_mm3=volume(intersection),original_AA_front_common_mm3=common(shape,old),new_lip_common_mm3=common(shape,lip)))
    result=dict(status='DIAGNOSTIC_COMPLETE_NOT_A_RELEASE',rows=records,source=ref(source),producer=ref(out/'producer.py'),interpretation='Separate original-front interference from added finite-lip interference before choosing a geometric correction.')
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
