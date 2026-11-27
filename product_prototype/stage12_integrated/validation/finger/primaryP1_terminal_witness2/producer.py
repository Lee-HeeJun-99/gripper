"""Locate exact P1 terminal residual intersection and cross-section extrema."""
import json,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump
from verify_primary_finger_v5 import sectors,independent,LR,ANCHOR
from primary_module_design import tr,Ry
from incremental_stage1 import read,bounds,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from scipy.optimize import minimize_scalar
import primary_finger_equilibrium_v5 as m
from rod_point_jacobian import walls
out=ROOT/'validation/finger'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'validation/finger/primaryP1_operating4/cases.json';row=next(r for r in json.loads(src.read_text()) if r['n']==32 and r['T_N']==1)
cad=json.loads((ROOT/'cad/exports/primaryP1_open9/summary.json').read_text());f=REPO/cad['part_references']['F0_TERMINAL_FRONT']['path'];front=read(f)
a=row['rail_angles_rad'][-1];R=Ry(a);end=np.array([row['rail_tip_m'][0]*1000,0,row['rail_tip_m'][1]*1000]);shift=end-R@np.array([50.4,0,-84]);hits=[]
for i,s in enumerate(sectors(row)):
 q=BRepAlgoAPI_Common(tr(s,R.T,-R.T@shift),front).Shape();v=volume(q)
 if v>1e-10:
  g=GProp_GProps();BRepGProp.VolumeProperties_s(q,g,1e-11);hits.append(dict(segment=i,common_mm3=v,bounds_mm=bounds(q),centroid_mm=[g.CentreOfMass().X(),g.CentreOfMass().Y(),g.CentreOfMass().Z()]))
v=np.array(row['state']);r,p,rt,pt,er,ep,M,*_=m.state(v,32)
def point(s,side):
 p,a=m.rod(v[64:],m.LP,32,True,[s])[0];return M.T@(p+side*.00015*np.array([-np.cos(a),np.sin(a)])-r[-1])+[.0504,-.084]
rows=[]
for side in [-1,1]:
 for j in range(3):
  fun=lambda s:walls(point(s,side),np.array([-.03363880995252074,-.095]),.08350880995252075)[0][j]
  for i in range(28,32):
   opt=minimize_scalar(fun,bounds=(i*m.LP/32,(i+1)*m.LP/32),method='bounded',options={'xatol':1e-16});rows.append(dict(side=side,wall=j,segment=i,s_m=opt.x,gap_m=opt.fun,local_mm=(point(opt.x,side)*1000).tolist()))
dump(out/'summary.json',dict(status='ACTUAL_P1_TERMINAL_RESIDUAL_LOCATED',candidate=ref(ROOT/'cad/exports/primaryP1_open9/summary.json'),source=ref(src),front=ref(f),hits=hits,wall_minima=rows,whole_system_release=False));print(json.dumps(dict(hits=hits,negative=[r for r in rows if r['gap_m']<-1e-10])))
