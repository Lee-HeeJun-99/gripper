"""Independent actual STEP cylinder axes/radii versus analytical funnel model."""
import argparse,json,math,sys,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Cylinder
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAD_funnel1/summary.json';case=json.loads(source.read_text());f=case['funnel_profile'];rows=[]
    for i in range(3):
        angle=i*2*math.pi/3;R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
        centre=R@np.array([f['center_X_mm'],0,f['center_Z_mm']]);axis=R@np.array([0.,1.,0.]);file=ROOT/'cad/exports/revAD_funnel1'/f'F{i}_TERMINAL_FRONT.step';shape=read(file);it=TopExp_Explorer(shape,TopAbs_FACE);found=[]
        while it.More():
            s=BRepAdaptor_Surface(TopoDS.Face_s(it.Current()))
            if s.GetType()==GeomAbs_Cylinder:
                c=s.Cylinder()
                if c.Radius()>50:
                    p=c.Axis().Location();direction=c.Axis().Direction();origin=np.array([p.X(),p.Y(),p.Z()]);direction=np.array([direction.X(),direction.Y(),direction.Z()]);d=origin-centre
                    found.append(dict(radius_mm=c.Radius(),radius_error_mm=abs(c.Radius()-f['radius_mm']),axis_error=float(1-abs(direction@axis)),axis_line_distance_mm=float(np.linalg.norm(d-axis*(d@axis)))))
            it.Next()
        rows.append(dict(part=f'F{i}_TERMINAL_FRONT',STEP=ref(file),actual_cylindrical_faces=found,status='PASS' if found and all(r['radius_error_mm']<1e-7 and r['axis_error']<1e-10 and r['axis_line_distance_mm']<1e-7 for r in found) else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',scope='ACTUAL THREE STEP FUNNEL CYLINDER / ANALYTICAL MODEL IDENTITY ONLY',rows=rows,candidate=ref(source),producer=ref(out/'producer.py'),stage1_release=False,stage2_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
