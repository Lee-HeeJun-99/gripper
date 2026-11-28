"""Review image tessellated directly from actual P1 STEP, display subset only."""
import sys,json,shutil,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
out=ROOT/'validation/integrated/primaryP1_review61c';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_splitpin61c/summary.json';cad=json.loads(cp.read_text());ids=['BENCH_SUPPORT','EXTERNAL_BENCH_PLATE','F0_MICRO_MOTOR','F0_STOCK_HUB','F0_SPOOL','MOTOR_CAP','F0_ROOT_BACK','F0_ROOT_FRONT','F0_RAIL_L','F0_RAIL_R','F0_SKIN','F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_TENDON_WIRE'];ids += [n for n in cad['part_references'] if 'SOCKET_KEEPER' in n or n.startswith(('F0_RF','MOTOR_CAP_BOLT','MOTOR_CAP_NUT'))];meshes={}
for n in ids:
 assert not(ROOT/'runtime/STOP').exists();r=cad['part_references'][n];assert sha(REPO/r['path'])==r['SHA256'];s=read(REPO/r['path']);BRepMesh_IncrementalMesh(s,.18,False,.4,True).Perform();tris=[];ex=TopExp_Explorer(s,TopAbs_FACE)
 while ex.More():
  f=TopoDS.Face_s(ex.Current());ex.Next();loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(f,loc)
  if tri is None:raise RuntimeError('missingtriangulation')
  pp=[]
  for k in range(1,tri.NbNodes()+1):
   q=tri.Node(k).Transformed(loc.Transformation());pp.append([q.X(),q.Y(),q.Z()])
  pp=np.array(pp)
  for k in range(1,tri.NbTriangles()+1):tris.append(pp[np.array(tri.Triangle(k).Get())-1])
 meshes[n]=np.array(tris)
fig=plt.figure(figsize=(13,6));axes=[fig.add_subplot(121,projection='3d'),fig.add_subplot(122,projection='3d')]
for ai,ax in enumerate(axes):
 for n,tri in meshes.items():
  if ai==1 and n=='EXTERNAL_BENCH_PLATE':continue
  color='#e63946' if 'SOCKET_KEEPER' in n else '#607d8b' if n=='BENCH_SUPPORT' else '#aaa' if n=='EXTERNAL_BENCH_PLATE' else '#d62828' if n=='F0_TENDON_WIRE' else '#f6aa1c' if n in ['F0_RAIL_L','F0_RAIL_R','F0_SKIN'] else '#2a9d8f' if n in ['F0_MICRO_MOTOR','F0_STOCK_HUB','F0_SPOOL','MOTOR_CAP'] else '#9b5de5';alpha=.24 if n=='BENCH_SUPPORT' else .30 if n=='EXTERNAL_BENCH_PLATE' else .95;ax.add_collection3d(Poly3DCollection(tri,facecolors=color,edgecolors='none',alpha=alpha))
 ax.view_init(elev=18 if ai==0 else 10,azim=-60);ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm')
 if ai==0:ax.set(xlim=(-130,170),ylim=(-100,90),zlim=(-145,60));ax.set_box_aspect((300,190,205));ax.set_title('83-shape P1 specimen with installed split-pin design geometry')
 else:ax.set(xlim=(-16,78),ylim=(-39,24),zlim=(-14,39));ax.set_box_aspect((94,63,53));ax.set_title('Retained keepers and new split pins (red)')
fig.suptitle('Actual STEP geometry — P1 splitpin61c\nDisplay subset; Nominal proposed pin eye/splayed legs; source size only; no operating/strength claim');fig.tight_layout();fig.savefig(out/'actual_CAD_review.png',dpi=160);plt.close(fig);dump(out/'summary.json',dict(status='ACTUAL_P1_STEP_TESSELLATED_REVIEW_IMAGE_NOT_PHYSICAL_VALIDATION',candidate=ref(cp),producer=ref(out/'producer.py'),image=ref(out/'actual_CAD_review.png'),displayed_part_IDs=ids,actual_full_part_count=83,omitted_part_IDs=[n for n in cad['part_references'] if n not in ids],triangles={n:len(t) for n,t in meshes.items()},whole_system_release=False,newly_qualified_system_gate_ids=[]));print('Actual STEP review image written')
