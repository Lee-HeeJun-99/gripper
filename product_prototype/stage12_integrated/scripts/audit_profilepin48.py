"""Independent geometry/work bounds and continuous specified assembly envelopes.
No material/operating equilibrium is inferred from geometric contacts.
"""
import json,sys,shutil,math
import numpy as np
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,box,cyl,fuse,volume
from mechanisms_stage1 import hex_axis
from primary_socketcage47d import STATIONS
from validate_nutseat46c import rotate

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_profilepin48b_independent';out.mkdir();shutil.copyfile(__file__,out/'auditor.py');cp=ROOT/'cad/exports/primaryP1_profilepin48b/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(s) for n,s in parts.items()};pins={n for n in parts if '_SPLIT_PIN_' in n};rows=[];sweeps=[];poses=[];torques=[]
 def hits(sh,excluded):
  b=bounds(sh);return [dict(part_ID=n,common_mm3=v) for n,s in parts.items() if n not in excluded and overlap(b,bb[n]) and (v:=common(sh,s))>1e-8]
 for prefix,i,x,y,seat,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();kn=f'{prefix}_SOCKET_KEY_{i}';pn=f'{prefix}_SPLIT_PIN_{i}';bn=f'{prefix}_BOLT_{i}';z=seat+8.2
  # Independent circular-segment section integrals and all-angle bounds.
  from scipy.integrate import quad
  from scipy.optimize import minimize_scalar
  rr=.9;gg=.05;rad=3.;ll=5.8;amax=math.pi/4
  area=quad(lambda u:2*math.sqrt(rr*rr-u*u),gg,rr,epsabs=1e-12)[0]
  cc=quad(lambda u:2*(u-gg)*math.sqrt(rr*rr-u*u),gg,rr,epsabs=1e-12)[0]/area
  # For each leg material ordinate u in [0,rr-gg],theta in [0,alpha]:
  # bend x=(rad-u)sin(theta), y=gg+rad-(rad-u)cos(theta).
  # Straight part end uses length ll-(rad-cc)*alpha. Max y occurs at crown.
  endy=lambda aa:gg+rad-(rad-(rr-gg))*math.cos(aa)+(ll-(rad-cc)*aa)*math.sin(aa)
  opt=minimize_scalar(lambda aa:-endy(aa),bounds=(0,amax),method='bounded',options={'xatol':1e-14})
  ymax=max(endy(0),endy(amax),endy(opt.x))+1e-8
  # Flat-reference arclength bounds all x; inner radius remains positive.
  xmax=ll+cc*amax+1e-8;hh=math.sqrt(rr*rr-gg*gg)
  formenv=box(x+7.2,y-ymax,z-hh,xmax,2*ymax,2*hh)
  sweeps.append(dict(operation='continuous_all_angle_full_profile_tail_form_and_unform',part=pn,alpha_range_rad=[0,amax],material_ordinate_mm=[0,rr-gg],x_range_relative_mm=[7.2,7.2+xmax],y_range_relative_mm=[-ymax,ymax],z_halfheight_mm=hh,independent_section_area_mm2=area,independent_centroid_from_flat_mm=cc,hits=hits(formenv,{pn}),proof='Exact planar circular bend plus tangent straight leg;0<=theta<=alpha<=pi/4;radius-u>0;conservative x from arclength;bounded analytic crown y maximum;not plier mechanics/material certification'))
  # Conservative envelopes of all translated points,not sparse pose inference.
  keyenv=fuse(box(x-4.5,y-4.5,seat+5.2,9,9,31),hex_axis((x,y,seat+2.6),(0,0,1),3.9,27.7))
  sweeps.append(dict(operation='continuous25mm_key_top_feed',part=kn,hits=hits(keyenv,pins|{kn})))
  shaft=cyl(.9,(x-32.2,y,z),45.2,(1,0,0))
  eye=fuse(fuse(cyl(1.8,(x-33.9,y,z-.9),1.8),cyl(1.8,(x-8.9,y,z-.9),1.8)),box(x-33.9,y-1.8,z-.9,25,3.6,1.8))
  sweeps.append(dict(operation='continuous25mm_straightpin_horizontal_feed',part=pn,hits=hits(fuse(shaft,eye),pins)))
  # Vertical staging of straight pin at x offset -25mm,then horizontal feed.
  def stadium_z(x0,L,r):
   return fuse(fuse(cyl(r,(x0,y,z),L,(1,0,0)),cyl(r,(x0,y,z+25),L,(1,0,0))),box(x0,y-r,z,L,2*r,25))
  env=fuse(stadium_z(x-32.2,20.2,.9),cyl(1.8,(x-33.9,y,z-.9),26.8))
  sweeps.append(dict(operation='continuous25mm_vertical_pin_staging',part=pn,hits=hits(env,pins)))
  # Bolts are inserted and tightened BEFORE keys/pins;the original driver remains removable.
  driver=hex_axis((x,y,seat+2.6),(0,0,1),3.9,32)
  poses.append(dict(operation='original4AF_driver_before_key',part=bn,hits=hits(driver,pins|{kn})))
  # Independent clipped rotated square analytic area vs actual intersection.
  # Cage side planes x=+/-4.1; square8x8 and depth6 provide exact volume.
  a=math.pi/4-math.acos(4.6/(4.5*math.sqrt(2)))
  def clip(poly,axis,sgn,limit):
   result=[]
   for j,p in enumerate(poly):
    q=poly[(j+1)%len(poly)];dp=sgn*p[axis]-limit;dq=sgn*q[axis]-limit
    if dp<=0:result.append(p)
    if (dp<=0)!=(dq<=0):result.append(p+(q-p)*(-dp/(dq-dp)))
   return result
  for sign in [-1,1]:
   t=sign*(a+.002);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);poly=[R@np.array(p) for p in [(-4.5,-4.5),(4.5,-4.5),(4.5,4.5),(-4.5,4.5)]];inside=poly
   # Two x cheeks only at mount;through pocket also y walls. Use each cheek actual contact separately via slab.
   analytic=0.
   for side in [-1,1]:
    pol=clip(poly,0,-side,-4.6)
    area=abs(sum(np.cross(pol[j],pol[(j+1)%len(pol)]) for j in range(len(pol)))/2) if len(pol)>2 else 0
    analytic+=area*6
   s=rotate(parts[kn],x,y,t)
   slab=fuse(box(x-7,y-5,seat+5.2,2.4,10,6),box(x+4.6,y-5,seat+5.2,2.4,10,6))
   actual=common(s,slab)
   rows.append(dict(key=kn,sign=sign,analytic_stop_rad=sign*a,probe_angle_rad=t,analytic_two_xwall_mm3=float(analytic),actual_two_xwall_mm3=actual,error_mm3=abs(float(analytic)-actual)))
   # Two opposing x wall forces at actual square corners give a pure z couple.
   # Unit screw axial load F needs kF torque at socket and receiver.
   lever=4.5*(math.cos(a)-math.sin(a));k=.8/(2*math.pi);f=k/(2*lever)
   p=np.array([[4.6,-sign*lever,0],[-4.6,sign*lever,0]]);forces=np.array([[-sign*f,0,0],[sign*f,0,0]])
   moment=np.cross(p,forces).sum(axis=0);net=forces.sum(axis=0)
   torques.append(dict(key=kn,sign=sign,load_definition='unit1N axial screw force contrast;NOT100goperatingtendonload',required_torque_Nmm=k,contact_points_relative_mm=p.tolist(),contact_forces_N=forces.tolist(),net_force_N=net.tolist(),reaction_moment_Nmm=moment.tolist(),torque_magnitude_error_Nmm=abs(abs(float(moment[2]))-k),virtual_work_Nmm_per_rad=float(moment[2]),point_corner_pressure_MPa=None,capacity_N=None))
 old=json.loads((ROOT/'cad/exports/primaryP1_nutseat46b/summary.json').read_text());delta=[]
 for n in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT']:
  vo=volume(read(REPO/old['part_references'][n]['path']));vn=volume(parts[n]);delta.append(dict(part=n,old_volume_mm3=vo,new_volume_mm3=vn,delta_mm3=vn-vo,physical_mass_kg=None))
 # Explicit whole-product freebody:internal additions cannot support external force.
 # Sum of internal contact forces cancels;normalfloor reaction has no x/y/yaw.
 freebody=dict(external_unit_horizontal_force_N=[1,0,0],normal_only_floor_can_balance=False,external_plate_fixed=False,new_cage_contacts_are_internal=True,ultimate_external_attachment=None,actual_operating_equilibrium_count=0)
 checks=dict(all_hashes_bound=True,all_continuous_specified_envelopes_clear=all(not r['hits'] for r in sweeps),original_driver_access_before_keys=all(not r['hits'] for r in poses),analytic_BRep_two_wall_volume=all(r['error_mm3']<1e-7 for r in rows),actual_corner_force_couple_balance=all(max(abs(v) for v in r['net_force_N'])<1e-12 and r['torque_magnitude_error_Nmm']<1e-12 for r in torques),free_whole_product_still_explicitly_fails=True)
 result=dict(status='ACTUAL_P1_PROFILE_PIN_CONTINUOUS_ENVELOPES_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_PROFILE_PIN_CONTINUOUS_ENVELOPES_FAIL',candidate=ref(cp),auditor=ref(out/'auditor.py'),checks=checks,continuous_envelopes=sweeps,driver_poses=poses,independent_square_clipping=rows,conditional_actual_corner_reaction=torques,changed_support_volumes=delta,whole_product_freebody=freebody,actual_parts=len(parts),accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Conservative translation and mathematical fullprofile bend/unbend envelopes;not material plasticforming/contact/toolcapacity or threadhelicalassembly certification','Point/corner normal reactions have no finite pressure capacity;no admissible material bound or real operatingload imposed','Changed receiver/stand invalidate oldphysicalfields;sourcefit/effectiveengagement/strength/globalenergy and ultimateexternalattachment remain blocked'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failed_sweeps=[r for r in sweeps+poses if r['hits']],maxvolumeerror=max(r['error_mm3'] for r in rows))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
