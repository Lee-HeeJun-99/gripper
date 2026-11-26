"""Exact annular-sector envelopes, no ruled-loft chord penetration artefact.
Constant maximum width on each segment conservatively contains actual taper.
This proves only stored circular-arc coupon shapes against actual terminal CAD.
"""
import argparse,json,math,shutil,sys
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,volume
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Circ,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
def sectors(q,L):
    q=np.r_[0.,q];h=L/(len(q)-1);p=np.array([0.,.00025]);result=[]
    for i in range(len(q)-1):
        d=q[i+1]-q[i];k=d/h;w=12-.06*(7+i*h*1000)
        if abs(k)<1e-10:raise ValueError('Exact straight-sector branch not implemented; no approximation hidden')
        centre=p+np.array([-math.sin(q[i]),math.cos(q[i])])/k;radius=1000/k
        axis=gp_Ax2(gp_Pnt(50.4-centre[1]*1000,-w,-7-centre[0]*1000),gp_Dir(0,1,0),gp_Dir(1,0,0))
        shift=math.pi if radius<0 else 0;lo,hi=sorted((q[i]+shift,q[i+1]+shift));ri,ro=sorted((abs(radius-.15),abs(radius+.15)))
        outer=BRepBuilderAPI_MakeEdge(gp_Circ(axis,ro),float(lo),float(hi)).Edge();inner=BRepBuilderAPI_MakeEdge(gp_Circ(axis,ri),float(lo),float(hi)).Edge()
        # Endpoint construction independent of edge vertex ordering.
        c=np.array([axis.Location().X(),-w,axis.Location().Z()])
        def endpoint(r,t):return gp_Pnt(*(c+np.array([r*math.cos(t),0.,-r*math.sin(t)])))
        a=BRepBuilderAPI_MakeEdge(endpoint(ro,hi),endpoint(ri,hi)).Edge();b=BRepBuilderAPI_MakeEdge(endpoint(ri,lo),endpoint(ro,lo)).Edge()
        wire=BRepBuilderAPI_MakeWire();wire.Add(outer);wire.Add(a);wire.Add(inner.Reversed());wire.Add(b)
        face=BRepBuilderAPI_MakeFace(wire.Wire()).Face();s=BRepPrimAPI_MakePrism(face,gp_Vec(0,2*w,0)).Shape()
        assert BRepCheck_Analyzer(s).IsValid();result.append(s)
        p+=h*np.sinc(d/(2*np.pi))*np.array([math.cos((q[i+1]+q[i])/2),math.sin((q[i+1]+q[i])/2)])
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--input',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/finger'/a.input/'summary.json';data=json.loads(source.read_text());frontpath=ROOT/'cad/exports'/a.candidate/'F0_TERMINAL_FRONT.step';backpath=S1/'cad/parts/revAA_mbd1/F0_TERMINAL_BACK.step';front,back=read(frontpath),read(backpath);rows=[]
    for row in data['rows']:
        if row['n']!=32:continue
        t=math.radians(row['fixture_angle_deg']);R=.088/t;c,s=math.cos(t),math.sin(t);M=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        end=np.array([50.4-R*(1-c)*1000,0,-7-R*s*1000]);shift=end-M@np.array([50.4,0,-95.]);T=gp_Trsf();T.SetValues(*[float(v) for i in range(3) for v in (*M[i],shift[i])]);T.Invert()
        records=[]
        for i,sector in enumerate(sectors(row['state_angles_rad'],data['PET_free_length_m'])):
            local=BRepBuilderAPI_Transform(sector,T,True).Shape();vf,vb=common(local,front),common(local,back)
            records.append(dict(segment=i,front_common_mm3=vf,back_common_mm3=vb))
        rows.append(dict(angle_deg=row['fixture_angle_deg'],status='PASS' if all(abs(r['front_common_mm3'])<1e-8 and abs(r['back_common_mm3'])<1e-8 for r in records) else 'FAIL',segments=records))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',scope='EXACT CIRCULAR ARC / MAX-WIDTH ENVELOPE vs ACTUAL FRONT/BACK, STORED32SEGMENT FIXTURE STATES ONLY',rows=rows,source=ref(source),front=ref(frontpath),back=ref(backpath),producer=ref(out/'producer.py'),
        tolerance_common_mm3=1e-8,product_release=False,limitations=['No solved flexible rail, friction, stock/trajectory uncertainty or dynamic proof','Max-width envelope can conservatively reject a tapered shape; no width is reduced to hide collision'])
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
