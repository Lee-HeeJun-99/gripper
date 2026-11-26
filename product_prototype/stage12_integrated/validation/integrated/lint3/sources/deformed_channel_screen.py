"""Actual terminal BRep versus reconstructed finite-PET coupon shapes.
Lofted sampled shape / prescribed circular rail fixture, not whole dynamics.
No nominal component is removed to hide overlap; front AND back are checked.
"""
import argparse,json,math,sys,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,S2,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,volume
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.gp import gp_Pnt,gp_Trsf,gp_Mat,gp_XYZ
def pet(q,L,sub):
    q=np.r_[0.,q];n=len(q)-1;h=L/n;p=np.array([0.,.00025]);loft=BRepOffsetAPI_ThruSections(True,True,1e-9)
    for i in range(n):
        for t in np.linspace(0,1,sub+1) if i==n-1 else np.linspace(0,1,sub+1)[:-1]:
            d=(q[i+1]-q[i])*t;a=q[i]+d/2
            xy=p+h*t*np.sinc(d/(2*np.pi))*np.array([math.cos(a),math.sin(a)])
            angle=q[i]+d;s=h*(i+t);w=(12-.06*(7+s*1000))
            c=np.array([50.4-xy[1]*1000,0.,-7-xy[0]*1000]);normal=np.array([-math.cos(angle),0.,math.sin(angle)])
            wire=BRepBuilderAPI_MakePolygon()
            for thick,y in [(-.15,-w),(.15,-w),(.15,w),(-.15,w)]:
                x=c+thick*normal+np.array([0.,y,0.]);wire.Add(gp_Pnt(*x))
            wire.Close();loft.AddWire(wire.Wire())
        d=q[i+1]-q[i];a=(q[i+1]+q[i])/2;p+=h*np.sinc(d/(2*np.pi))*np.array([math.cos(a),math.sin(a)])
    loft.Build();assert loft.IsDone();return loft.Shape()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--input');p.add_argument('--candidate');p.add_argument('--meshes',nargs='+',type=int,default=[32]);a=p.parse_args()
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    paths=[ROOT/'validation/finger/finite_pet2/summary.json',ROOT/'validation/finger/finite_pet_AC1/summary.json']
    if a.input:paths=[ROOT/'validation/finger'/a.input/'summary.json']
    frontpath=ROOT/'cad/exports'/a.candidate/'F0_TERMINAL_FRONT.step' if a.candidate else S2/'revised_cad/revAB_sliding_pet1/F0_TERMINAL_FRONT.step'
    front=read(frontpath);back=read(S1/'cad/parts/revAA_mbd1/F0_TERMINAL_BACK.step');records=[]
    for source in paths:
        data=json.loads(source.read_text());L=data.get('PET_free_length_m',.0874)
        for row in data['rows']:
            if row['n'] not in a.meshes:continue
            theta=math.radians(row['fixture_angle_deg']);R=.088/theta;c,s=math.cos(theta),math.sin(theta)
            M=np.array([[c,0,s],[0,1,0],[-s,0,c]])
            end=np.array([50.4-R*(1-c)*1000,0,-7-R*s*1000]);shift=end-M@np.array([50.4,0,-95.])
            tr=gp_Trsf();tr.SetValues(*[float(x) for i in range(3) for x in (*M[i],shift[i])])
            fixtures={name:BRepBuilderAPI_Transform(shape,tr,True).Shape() for name,shape in [('front',front),('back',back)]}
            for sub in (2,4):
                shape=pet(row['state_angles_rad'],L,sub);assert BRepCheck_Analyzer(shape).IsValid()
                hits={name:common(shape,body) for name,body in fixtures.items()}
                records.append(dict(source=ref(source),angle_deg=row['fixture_angle_deg'],PET_length_m=L,subdivisions_per_segment=sub,
                    PET_volume_mm3=volume(shape),terminal_common_mm3=hits,status='PASS' if all(abs(v)<1e-8 for v in hits.values()) else 'FAIL'))
    result=dict(status='PASS' if records and all(r['status']=='PASS' for r in records) else 'FAIL',scope='ACTUAL FRONT/BACK vs RECONSTRUCTED PET GEOMETRY ON PRESCRIBED CIRCULAR FIXTURE ONLY',
        rows=records,front=ref(frontpath),back=ref(S1/'cad/parts/revAA_mbd1/F0_TERMINAL_BACK.step'),producer=ref(out/'producer.py'),
        limitations=['Ruled loft interpolation, not continuous curved-solid collision proof','No actual flexible-rail dynamics, friction or finite shell','No whole assembly Stage1 revalidation or release','Projected endpoint-channel constraints do not replace finite 3D channel verification'])
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
