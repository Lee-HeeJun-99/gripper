"""Independent STEP reimport and finite D-shaft contact/backlash controls."""
import json,sys,math,shutil
import numpy as np
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,box,cut,common,translate,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
out=ROOT/'validation/transmission/AL_Ddrive_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
assert not (ROOT/'runtime/STOP').exists()
src=ROOT/'cad/exports/revAL_Ddrive1/summary.json';d=json.loads(src.read_text())
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
hub=read(REPO/d['part_references']['F0_CLUTCH_INPUT_HUB']['path']);motor=read(REPO/d['part_references']['F0_MOTOR']['path'])
checks=dict(single_valid_solid=BRepCheck_Analyzer(hub).IsValid() and solid_count(hub)==1,source_hashes=True,nominal_motor_clear=common(hub,motor)<1e-8)
# STL closed manifold edge multiplicity, quantized at exporter precision.
for i in range(3):
 p=ROOT/f'cad/exports/revAL_Ddrive1/F{i}_CLUTCH_INPUT_HUB.stl';verts=[]
 for line in p.read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(v),9) for v in line.split()[1:]))
 edges={}
 for j in range(0,len(verts),3):
  t=verts[j:j+3]
  for a,b in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])):
   key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
 checks[f'F{i}_closed_STL']=bool(edges) and all(n==2 for n in edges.values())
rows=[]
for r in (2.494,2.5):
 for across in (4.4,4.6):
  a=across-r;b=math.sqrt(r*r-a*a);c=2.13
  angle=brentq(lambda t:a*math.cos(t)+b*math.sin(t)-c,0,math.acos(a/r))
  shaft=cut(cyl(r,(110,4.8,20),9.7,(0,1,0)),box(110+a,4.7,16,4,10,8))
  vals=[]
  for sign in (-1,1):
   volumes=[]
   for factor in (.9,1.1):
    tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(110,0,20),gp_Dir(0,1,0)),sign*angle*factor)
    volumes.append(common(hub,BRepBuilderAPI_Transform(shaft,tr,True).Shape()))
   vals.append(dict(sign=sign,before_mm3=volumes[0],after_mm3=volumes[1]))
  lever=b*math.cos(angle)-a*math.sin(angle)
  passed=all(v['before_mm3']<1e-8 and v['after_mm3']>1e-8 for v in vals) and lever>0
  rows.append(dict(radius_mm=r,across_mm=across,backlash_one_side_deg=math.degrees(angle),normal_torque_arm_mm=lever,finite_BRep=vals,passed=passed))
checks['both_signs_all_dimension_corners']=all(x['passed'] for x in rows)
path=[dict(shift_Y_mm=y,common_mm3=common(translate(hub,0,y,0),motor)) for y in (0,2,5,12,20)]
checks['motor_only_insertion_samples']=all(x['common_mm3']<1e-8 for x in path)
# A circular bore cannot produce this early finite angular stop: negative control.
circular=cut(cyl(4,(110,4.8,20),11.2,(0,1,0)),cyl(2.52,(110,4.7,20),11.4,(0,1,0)))
checks['circular_negative_control']=common(circular,shaft)<1e-8
result=dict(status='FINITE_D_DRIVE_VERIFICATION_PASS' if all(checks.values()) else 'FINITE_D_DRIVE_VERIFICATION_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),checks=checks,cases=rows,motor_only_insertion=path,scope='Finite changed STEP and closed STL; dimension-corner angular stop with nonzero torque arm, motor-only sampled insertion. No loaded capacity or full assembly-path certificate.',axial_capture=False,whole_system_release=False)
dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if all(checks.values()) else 2)
