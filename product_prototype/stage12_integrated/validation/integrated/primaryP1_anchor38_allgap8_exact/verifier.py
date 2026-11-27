"""Actual CAD-clipped common-face continuous affine-gap bounds.
Independently rebuilds finite contact faces/partition and triangle intersection.
Exact analytic BRep optimal bounds include curved trim,not only vertices.
No contact producer/FEMassembler/optimizer import.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,bounds
from primary_motor_bearing_wrenches import faces
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt,gp_Trsf

def area_centroid(s):
 g=GProp_GProps();BRepGProp.SurfaceProperties_s(s,g);q=g.CentreOfMass();return g.Mass(),np.array([q.X(),q.Y(),q.Z()])
def triangle(x):
 wire=BRepBuilderAPI_MakePolygon()
 for q in x:wire.Add(gp_Pnt(*map(float,q)))
 wire.Close();return BRepBuilderAPI_MakeFace(wire.Wire()).Face()
def rebuilt_faces(shapes):
 out=[]
 for axis,value,d,label in [(2,66,[0,0,-1],'topseat'),(0,-50,[1,0,0],'key0_xmin'),(0,-38,[-1,0,0],'key0_xmax'),(1,28,[0,1,0],'key_ymin'),(1,40,[0,-1,0],'key_ymax')]:
  other=[k for k in range(3) if k!=axis]
  for fa in faces(shapes[0],axis,value):
   for fb in faces(shapes[1],axis,value):
    f=BRepAlgoAPI_Common(fa,fb).Shape();ar,_=area_centroid(f)
    if ar<1e-8:continue
    bb=np.array(bounds(f));grid=[np.linspace(bb[k],bb[k+3],3) for k in other]
    for lo,hi in zip(grid[0][:-1],grid[0][1:]):
     for low,high in zip(grid[1][:-1],grid[1][1:]):
      corner=bb[:3].copy();size=bb[3:]-corner;corner[axis]-=.01;size[axis]=.02;corner[other]=[lo,low];size[other]=[hi-lo,high-low];s=BRepAlgoAPI_Common(f,box(*map(float,corner),*map(float,size))).Shape();a,c=area_centroid(s)
      if a>1e-8:out.append(dict(shape=s,label=label,axis=axis,n=np.array(d),area=a,centroid=c))
 return out

def scalar_bounds(shape,constant,gradient):
 length=float(np.linalg.norm(gradient))
 if length<1e-25:return float(constant),float(constant)
 u=gradient/length;aux=np.eye(3)[np.argmin(abs(u))];v=np.cross(u,aux);v/=np.linalg.norm(v);w=np.cross(u,v);tr=gp_Trsf();tr.SetValues(*[float(x) for row in [u,v,w] for x in [*row,0.]])
 transformed=BRepBuilderAPI_Transform(shape,tr,True).Shape();b=Bnd_Box();BRepBndLib.AddOptimal_s(transformed,b,False,False);q=b.Get();return float(constant+length*q[0]),float(constant+length*q[3])

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];d=json.loads((src/'summary.json').read_text());cad=json.loads((REPO/d['candidate']['path']).read_text());shapes=[read(REPO/cad['part_references'][n]['path']) for n in ['TEST_BASE','BENCH_ANCHOR_RAIL']];original=rebuilt_faces(shapes);old=ROOT/'validation/integrated/primaryP1_anchor37_fixed_h5_n2';old_d=json.loads((old/'summary.json').read_text());old_g=json.loads((REPO/old_d['geometry']['path']).read_text());assert len(original)==len(old_g['patches'])-3
 original_errors=[]
 for f,p in zip(original,old_g['patches'][:-3]):
  original_errors.append(dict(label=f['label'],label_matches=f['label']==p['label'],area_error_mm2=abs(f['area']-p['exact_CAD_area_mm2']),centroid_error_mm=float(np.linalg.norm(f['centroid']-p['exact_CAD_centroid_mm']))))
 assert all(x['label_matches'] and x['area_error_mm2']<1e-7 and x['centroid_error_mm']<1e-7 for x in original_errors)
 a=[dict(np.load(REPO/r['path'])) for r in d['fields']]
 for k,b in enumerate(a):
  if 'U' not in b:b['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
 ops=np.load(REPO/d['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);states=[]
 for row in d['rows']:
  ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None],rcond=1e-10);r=(scale*(T.T@lm)).reshape(2,6);U=[(b['U']@np.r_[row['contact_forces_N'],np.array(row['external_wrench_N_Nmm'])*(1 if k==0 else -1)]).reshape(-1,3) for k,b in enumerate(a)];states.append((row,U,r))
 e=json.loads((REPO/d['local_common_refinement']['path']).read_text());cells=[]
 for entry in e['patches']:
  f=original[entry['original_patch']];axis=f['axis'];xy=[k for k in range(3) if k!=axis];n=f['n']
  for saved in entry['cells']:
   assert not(ROOT/'runtime/STOP').exists();nodes=[saved['base_nodes'],saved['receiver_nodes']];x=[b['points_mm'][nd] for b,nd in zip(a,nodes)];s=BRepAlgoAPI_Common(BRepAlgoAPI_Common(f['shape'],triangle(x[0])).Shape(),triangle(x[1])).Shape();ar,c=area_centroid(s);results=[]
   for row,U,r in states:
    co=[]
    for k in range(2):
     values=(U[k][nodes[k]]+r[k,:3]+np.cross(r[k,3:],x[k]))@n;co.append(np.linalg.solve(np.c_[np.ones(3),x[k][:,xy]],values))
    coeff=co[0]-co[1];gradient=np.zeros(3);gradient[xy]=coeff[1:];lo,hi=scalar_bounds(s,coeff[0],gradient);results.append(dict(case=row['case'],continuous_affine_gap_lower_bound_mm=lo,continuous_affine_gap_upper_bound_mm=hi))
   cells.append(dict(original_patch=entry['original_patch'],base_nodes=nodes[0],receiver_nodes=nodes[1],actual_area_mm2=ar,recorded_area_mm2=saved['area_mm2'],area_error_mm2=abs(ar-saved['area_mm2']),centroid_error_mm=float(np.linalg.norm(c-saved['centroid_mm'])),states=results))
 minimum=min(r['continuous_affine_gap_lower_bound_mm'] for c in cells for r in c['states']);checks=dict(independent_original_partition=all(x['label_matches'] and x['area_error_mm2']<1e-7 and x['centroid_error_mm']<1e-7 for x in original_errors),actual_common_cell_area_centroid=all(c['area_error_mm2']<1e-7 and c['centroid_error_mm']<1e-7 for c in cells),all14_actual_selected_trimmed_faces_nonpenetrating=minimum>=-1e-8)
 dump(out/'summary.json',dict(status='ACTUAL_P1_SELECTED_CAD_TRIMMED_AFFINE_GAP_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_SELECTED_CAD_TRIMMED_AFFINE_GAP_FAIL',candidate=d['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),checks=checks,original_partition=original_errors,cells=cells,minimum_selected_exact_face_gap_mm=minimum,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ActualCADface intersected with both P1triangles,includingoriginalpartitionandcurvedtrims. OCPAddOptimalbounds after orthogonaltransformbound affinegap,not just sampledvertices.','Only selectedcells;uniformremainder contact not certified. FEcurvedvolumegeometry still linearfacet approximation.','Nominalzero-gapconditionalmaterial/source/boltmodel;no physicalexternalfixture,strength/globalenergy or operatingrelease.']))
 print(json.dumps(dict(checks=checks,cells=len(cells),minimum=minimum)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
