"""Actual positive P1 interfaces: finite-face frictionless necessary equilibrium.
No stiffness, pressure allowable, fit guarantee, or thread capacity is inferred.
"""
import json,sys,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,bounds,volume
from primary_contact_transfer_v3 import wrench
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def faces(s,axis,value):
 it=TopExp_Explorer(s,TopAbs_FACE);out=[]
 while it.More():
  f=TopoDS.Face_s(it.Current());b=bounds(f)
  if BRepAdaptor_Surface(f).GetType()==GeomAbs_Plane and abs(b[axis]-value)<1e-6 and abs(b[axis+3]-value)<1e-6:out.append(f)
  it.Next()
 return out

def patches(a,b,axis,value,direction,label):
 cells=[];other=[i for i in range(3) if i!=axis]
 for f in faces(a,axis,value):
  for g in faces(b,axis,value):
   p=BRepAlgoAPI_Common(f,g).Shape();prop=GProp_GProps();BRepGProp.SurfaceProperties_s(p,prop)
   if prop.Mass()<1e-8:continue
   bb=bounds(p);grids=[np.linspace(bb[i],bb[i+3],5) for i in other]
   for lo0,hi0 in zip(grids[0][:-1],grids[0][1:]):
    for lo1,hi1 in zip(grids[1][:-1],grids[1][1:]):
     xyz=np.array(bb[:3]);size=np.array(bb[3:])-xyz;xyz[axis]-=.01;size[axis]=.02
     xyz[other[0]]=lo0;size[other[0]]=hi0-lo0;xyz[other[1]]=lo1;size[other[1]]=hi1-lo1
     c=BRepAlgoAPI_Common(p,box(*map(float,xyz),*map(float,size))).Shape();q=GProp_GProps();BRepGProp.SurfaceProperties_s(c,q)
     if q.Mass()>1e-8:
      v=q.CentreOfMass();cells.append(dict(label=label,point_mm=[v.X(),v.Y(),v.Z()],area_mm2=q.Mass(),direction=direction))
 return cells

def gravity(s,rho):
 g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g);p=g.CentreOfMass();return wrench([p.X(),p.Y(),p.Z()],[0,0,-g.Mass()*1e-9*rho*9.80665])
def solve(cells,bolts,W,capW=None):
 meta=[];cols=[]
 for cell in cells:
  col=wrench(cell['point_mm'],cell['direction']);cap=-col if cell['label']=='motor_top' else np.zeros(6)
  cols.append(np.r_[col,cap] if capW is not None else col);meta.append(cell)
 for p in bolts:
  col=wrench(p,[0,0,-1]);cols.append(np.r_[np.zeros(6),col] if capW is not None else col);meta.append(dict(label='bolt_axial',point_mm=p,direction=[0,0,-1],area_mm2=None))
 A=np.array(cols).T;external=np.r_[W,capW] if capW is not None else W;scale=np.tile([1,1,1,100,100,100],len(external)//6)
 objective=np.ones(len(meta));result=linprog(objective,A_eq=scale[:,None]*A,b_eq=-scale*external,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 row=dict(success=bool(result.success),solver_status=int(result.status),solver_message=result.message,external_wrench_N_Nm=external.tolist(),variables=len(meta))
 if result.success:
  residual=(A@result.x+external).reshape(-1,6);rays=[dict(m,force_N=float(v),pressure_MPa=float(v/m['area_mm2']) if m['area_mm2'] else None) for m,v in zip(meta,result.x) if v>1e-12];row.update(rays=rays,force_error_N=float(np.linalg.norm(residual[:,:3],axis=1).max()),moment_error_Nm=float(np.linalg.norm(residual[:,3:],axis=1).max()),total_axial_bolt_N=sum(r['force_N'] for r in rays if r['label']=='bolt_axial'),total_contact_N=sum(r['force_N'] for r in rays if r['label']!='bolt_axial'))
 return row

def main():
 out=ROOT/'validation/transmission'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_interfaces17/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/refs[n]['path']) for n in ['F0_ROOT_BACK','OPEN_FRAME','F0_MICRO_MOTOR','MOTOR_CAP']};load=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';l=json.loads(load.read_text())['rows'][0]
 root=[]
 for ax,v,d,label in [(2,-7,[0,0,1],'root_seat'),(2,-9,[0,0,1],'key_floor'),(0,68,[-1,0,0],'existing_wall'),(0,60,[1,0,0],'key_xmin'),(0,66,[-1,0,0],'key_xmax'),(1,-6,[0,1,0],'key_ymin'),(1,6,[0,-1,0],'key_ymax')]:root+=patches(s['F0_ROOT_BACK'],s['OPEN_FRAME'],ax,v,d,label)
 motor=[]
 for ax,v,d,label in [(2,14,[0,0,1],'motor_bottom'),(0,-5,[1,0,0],'motor_xmin'),(0,5,[-1,0,0],'motor_xmax')]:motor+=patches(s['F0_MICRO_MOTOR'],s['OPEN_FRAME'],ax,v,d,label)
 motor+=patches(s['F0_MICRO_MOTOR'],s['MOTOR_CAP'],2,26,[0,0,-1],'motor_top')
 RW=np.array(l['Root_force_couple_XYZ_N_Nm']);RW[3:]+=np.cross(l['Root_reference_m'],RW[:3]);RW+=gravity(s['F0_ROOT_BACK'],7900)
 MW=np.array(l['Motor_force_couple_XYZ_N_Nm']);MW[3:]+=np.cross(l['Motor_reference_m'],MW[:3]);CW=gravity(s['MOTOR_CAP'],2700)
 rb=[[64,-16,-3],[64,16,-3]];mb=[[x,y,29] for x in (-7,7) for y in (-29.5,-13.5)]
 rows=dict(root=solve(root,rb,RW),motor_and_cap=solve(motor,mb,MW,CW),root_without_key=solve([p for p in root if not p['label'].startswith('key_')],rb,RW),motor_without_side_lands=solve([p for p in motor if not p['label'].startswith('motor_x')],mb,MW,CW))
 areas={label:sum(p['area_mm2'] for p in root+motor if p['label']==label) for label in set(p['label'] for p in root+motor)}
 checks=dict(root_frictionless_equilibrium=rows['root']['success'],motor_and_cap_frictionless_equilibrium=rows['motor_and_cap']['success'],existing_wall_without_key_test=rows['root_without_key']['success'],motor_side_omission_rejected=not rows['motor_without_side_lands']['success'],finite_positive_patches=all(v>0 for v in areas.values()))
 dump(out/'patches.json',dict(root=root,motor=motor));dump(out/'tractions.json',rows);dump(out/'inputs.json',dict(candidate=ref(src),loads=ref(load),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_contact_transfer_v3.py'),ref(S1/'scripts/incremental_stage1.py')],parts={n:refs[n] for n in s},criteria=dict(force_N=1e-8,moment_Nm=1e-10),density_scope='RootBack7900/Cap2700kg/m3 conditional. Motor/rotor/string/Finger weights already in corrected gravity ports. Connector selfweight split and full Frame compliance unresolved.',mu=0))
 result=dict(status='ACTUAL_P1_POSITIVE_INTERFACES_NECESSARY_WRENCH_PASS' if all(checks.values()) else 'ACTUAL_P1_POSITIVE_INTERFACES_WRENCH_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),patches=ref(out/'patches.json'),tractions=ref(out/'tractions.json'),areas_mm2=areas,checks=checks,rows={k:{a:b for a,b in v.items() if a!='rays'} for k,v in rows.items()},newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Necessary rigid equilibrium on finite actual subfaces with nonnegative uniform pressures,not unique elastic load or capacity','Nominal zero-gap only;0.02mm clearance removes side/key contact at unchanged pose and demands compliant displacement/contact solution','No physical gearbox land location/case allowable or guaranteed material/friction/preload/thread engagement','Lift-slide-lower assembly/process/tolerance and finite coupledFrame/Ground/Base/benchanchor remain independent gates','No historical mesh/time/energy failure cured; no physical assembly/full3Finger/Stage3'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
