"""Actual P1 pin section conservation, finite forming path, capture and unit-load section screening.
No ductility or strength allowable supplied; no physical operating-load claim.
"""
import json,sys,shutil,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,overlap,common,translate,volume,solid_count,fuse,box
from primary_profilepin48b import STATIONS,cotter,tail,R,GAP,BEND_R,LEG,ANGLE,AREA,CENTROID
from OCP.BRepCheck import BRepCheck_Analyzer
CAD=sys.argv[1] if len(sys.argv)>1 else 'primaryP1_profilepin48b'
TAG=sys.argv[2] if len(sys.argv)>2 else 'primaryP1_profilepin48b_validation'
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/TAG;out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports'/CAD/'summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};pins={n for n in parts if '_SPLIT_PIN_' in n};keys={n for n in parts if '_SOCKET_KEY_' in n};poses=[];forms=[];capture=[];sections=[]
 def hits(s,ex):
  b=bounds(s);return [dict(part_ID=n,common_mm3=v) for n,t in parts.items() if n not in ex and overlap(b,bb[n]) and (v:=common(s,t))>1e-8]
 A=AREA;c=CENTROID;Rn=BEND_R-c
 for a in [0,ANGLE/4,ANGLE/2,3*ANGLE/4,ANGLE]:
  for sign in [-1,1]:
   s=tail(7.2,0,0,sign,a);V=volume(s);sections.append(dict(angle_rad=a,sign=sign,BRep_volume_mm3=V,reference_material_volume_mm3=A*LEG,relative_volume_error=abs(V-A*LEG)/(A*LEG),valid=bool(BRepCheck_Analyzer(s).IsValid()),solids=solid_count(s),centroid_reference_curvature_per_mm=1/Rn if a else 0,outer_tensile_engineering_strain=c/Rn if a else 0,inner_compressive_engineering_strain=-(R-GAP/2-c)/Rn if a else 0,forming_allowable=None))
 for pre,i,x,y,seat,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();pn=f'{pre}_SPLIT_PIN_{i}';kn=f'{pre}_SOCKET_KEY_{i}';z=seat+8.2;pin=parts[pn];key=parts[kn]
  for a in [0,ANGLE/4,ANGLE/2,3*ANGLE/4,ANGLE]:
   s=cotter(x,y,z,a);forms.append(dict(pin=pn,angle_rad=a,valid=bool(BRepCheck_Analyzer(s).IsValid()),solids=solid_count(s),hits=hits(s,{pn}),volume_mm3=volume(s)))
  straight=cotter(x,y,z,0)
  for dx in [-25,-15,-8,-3,-1,0]:poses.append(dict(operation='straight_insert',pin=pn,offset_mm=dx,hits=hits(translate(straight,dx,0,0),pins)))
  for dz in [25,12,6,3,1,0]:poses.append(dict(operation='key_before_pin',pin=pn,offset_mm=dz,hits=hits(translate(key,0,0,dz),pins|{kn})))
  for sign in [-1,1]:
   tool=box(x+8,y+(1 if sign>0 else -5),z-1.1,5,4,15);poses.append(dict(operation='jaw_access_excluding_only_pins',pin=pn,side=sign,hits=hits(tool,pins)))
  capture.append(dict(pin=pn,key_014_mm3=common(translate(key,0,0,.14),pin),key_016_mm3=common(translate(key,0,0,.16),pin),pair_031_cage_mm3=common(translate(fuse(key,pin),0,0,.31),parts[parent]),left_05_cage_mm3=common(translate(pin,-.5,0,0),parts[parent]),right_05_cage_mm3=common(translate(pin,.5,0,0),parts[parent]),left_15_cage_mm3=common(translate(pin,-1.5,0,0),parts[parent]),right_15_cage_mm3=common(translate(pin,1.5,0,0),parts[parent])))
 # Conditional section mechanics only: 1N total axial key uplift shared equally by 2legs,
 # 2simple supports at cheek inner faces +/-4.6; central point load is worst span moment.
 # No adoption as actual bearing/contact solution, and no unspecified support strength.
 from scipy.integrate import quad
 span=9.2;I=quad(lambda yy:2*(R*R-yy*yy)**1.5/3,GAP/2,R,epsabs=1e-13)[0];Z=I/math.sqrt(R*R-(GAP/2)**2);Pleg=.5
 screening=dict(total_key_uplift_N=1,load_status='UNIT_SECTION_SCREEN_NOT_OPERATING_LOAD',two_legs=True,semicircle_area_mm2=A,semicircle_centroid_from_flat_mm=c,section_I_about_horizontal_diameter_mm4=I,section_Z_mm3=Z,support_span_mm=span,per_leg_max_M_Nmm=Pleg*span/4,per_leg_nominal_max_bending_MPa=Pleg*span/4/Z,per_leg_support_average_shear_MPa=Pleg/2/A,material_minimum_MPa=None,capacity_N=None,actual_pressure_solution=None,actual_operating_equilibrium=False)
 checks=dict(all128hashes_bound=len(parts)==128,final_interferences_zero=not d['interferences'],changed_solids_valid_single=all(c['valid'] and c['solids']==1 for c in d['changed']),section_volume_preserved=all(r['relative_volume_error']<1e-8 for r in sections),all_bend_samples_valid_single=all(r['valid'] and r['solids']==1 for r in forms),all_bend_samples_clear=all(not r['hits'] for r in forms),assembly_samples_clear=all(not r['hits'] for r in poses),axial_capture=all(r['key_014_mm3']<1e-8 and r['key_016_mm3']>1e-8 and r['pair_031_cage_mm3']>1e-8 for r in capture),pin_capture_both_directions=all(r['left_15_cage_mm3']>1e-8 and r['right_15_cage_mm3']>1e-8 for r in capture))
 result=dict(status='ACTUAL_P1_CONSTANT_PROFILE_PIN_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_CONSTANT_PROFILE_PIN_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,sections=sections,forming_poses=forms,assembly_poses=poses,capture=capture,unit_section_screen=screening,maximum_volume_error=max(r['relative_volume_error'] for r in sections),forming_strain_model='Finite constant-curvature kinematic strain about semicircle centroid;not elastoplastic forming/springback or material certification',accepted_physical_product_equilibria=0,installed_capacity_N=None,whole_system_release=False,limitations=['Custom head ring retained;not exact supplier/ISO fullprofile','Constant section bent legs now explicit;forming samples are not continuous swept-material or plier mechanics certification','Bend neutral-axis/volume kinematic construction not material stress or minimum ductility','Unit uplift beam screen assumes support and equal sharing;no pressure/contact/allowable or actual100g load','Threadfit/capacity and ultimateexternalhost remain unqualified'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,max_volume_error=result['maximum_volume_error'],failed_forms=[r for r in forms if r['hits']],failed_poses=[r for r in poses if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
