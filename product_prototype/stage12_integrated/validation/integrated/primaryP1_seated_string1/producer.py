"""Spatial string on nominal tangent R11.00 floor, no unsupported radial lead.
Actual inherited nipple centre R11.25; smooth finite-width cylindrical contact.
"""
import sys,json,shutil
import numpy as np
from scipy.optimize import root
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_spatial_string import SpatialString
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
class SeatedString(SpatialString):
 def evaluate(self,z,details=False):
  pt,py,phi,l1,eta,dy=z;_,et=self.vec(np.pi/2-eta);h=self.R.T@(pt*et+py*self.a);zz=np.r_[h,0.,phi,l1,eta,dy]
  if not details:return super().evaluate(zz)[[0,1,2,5,6,7]]
  r=super().evaluate(zz,True);r['residual']=np.array(r['residual'])[[0,1,2,5,6,7]].tolist();r['solver_state']=z.tolist();return r
 def solve(self,seed):
  self.T=seed['T_N'];z=np.array([-seed['wire_start_tension_N'],0.,seed['drum_tangent_phi_rad'],seed['wire_free_length_m']*1000,seed['rotor_angle_rad'],0.]);sol=root(self.evaluate,z,tol=1e-10);r=self.evaluate(sol.x,True);r.update(root_success=bool(sol.success),root_message=str(sol.message),residual_max=float(np.max(abs(sol.fun))));r['checks']=dict(root_success=bool(sol.success),residual=r['residual_max']<1e-8,length_positive=min(r['contact_length_m'],r['free_length_m'])>0,compression=r['wrap_min_normal_N_per_m']>0,tension=r['minimum_tension_N']>0,flat_floor_axial=max(abs(np.array(r['wrap_local_axial_minmax_m'])))<.0002,ODE_success=r['ODE_success']);r['checks']={k:bool(v) for k,v in r['checks'].items()};return r

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();oldsrc=ROOT/'validation/integrated/primaryP1_spatial_floor2/summary.json';parent=json.loads(oldsrc.read_text());src=ROOT/'cad/exports/primaryP1_seated22/summary.json';cad=json.loads(src.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());oldinp=json.loads((REPO/parent['inputs']['path']).read_text());points=json.loads((REPO/oldinp['mass_points']['path']).read_text());spool=read(REPO/cad['part_references']['F0_SPOOL']['path']);g=GProp_GProps();BRepGProp.VolumeProperties_s(spool,g);co=g.CentreOfMass();p=next(p for p in points if p['part_ID']=='F0_SPOOL');before=dict(p);p.update(mass_kg=g.Mass()*1e-9*2700,rest_centroid_m=[co.X()*.001,co.Y()*.001,co.Z()*.001]);dump(out/'mass_points.json',points)
 seed=json.loads((REPO/oldinp['seed']['path']).read_text())[0];Rm=np.array(parent['motor_R']);C=np.array(parent['motor_C_m']);Rr=np.array(parent['root_R']);tr=np.array(parent['root_translation_m']);E0=np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]]);E=Rr@E0+tr;r=.01125
 a=SeatedString(points,Rm,C,E,r).solve(seed);b=SeatedString(points,Rm,C,E,r,32).solve(seed);zero=SeatedString(points,np.eye(3),np.array([0,0,.020]),E0,r).solve(seed);dump(out/'curves.json',{name:{k:row.pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')} for name,row in [('actual',a),('higher',b),('zero',zero)]})
 dump(out/'inputs.json',dict(candidate=ref(src),source=ref(oldsrc),seed=oldinp['seed'],mass_points=ref(out/'mass_points.json'),original_mass_points=oldinp['mass_points'],spool_mass_before=before,spool_mass_after=p,producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_spatial_string.py'),ref(S1/'scripts/incremental_stage1.py')]))
 result=dict(status='ACTUAL_P1_SEATED_SPATIAL_STRING_PARTIAL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),curves=ref(out/'curves.json'),actual=a,quadrature32=b,zero_support=zero,root_R=parent['root_R'],root_translation_m=parent['root_translation_m'],motor_R=parent['motor_R'],motor_C_m=parent['motor_C_m'],actual_wire_center_radius_m=r,quadrature_force_max_N=float(np.max(abs(np.array(a['Fe_N'])-b['Fe_N']))),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Same22changedspoolnominalseatandmass; one-way19elasticposes. No loadedfinitewireBRep/assembly/thread/strength/mesh/time/globalenergy/full3Fingercertificate.']);result['checks']=dict(actual=all(a['checks'].values()),higher=all(b['checks'].values()),zero=all(zero['checks'].values()),quadrature=result['quadrature_force_max_N']<1e-8);dump(out/'summary.json',result);print({k:v for k,v in result.items() if k not in ('actual','quadrature32','zero_support')});raise SystemExit(0 if all(result['checks'].values()) else 2)
if __name__=='__main__':main()
