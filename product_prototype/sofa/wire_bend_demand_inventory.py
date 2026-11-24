"""Actual saved centreline/section-rotation bend demand,NOT material strain/strength."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
csv.field_size_limit(16*1024*1024)
def curvature(points):
 a=np.diff(points,axis=0);d=np.linalg.norm(a[:-1],axis=1)*np.linalg.norm(a[1:],axis=1)*np.linalg.norm(a[:-1]+a[1:],axis=1)
 if np.any(d==0):raise ValueError('degenerate actual centreline;no artificial denominator floor')
 return 2*np.linalg.norm(np.cross(a[:-1],a[1:]),axis=1)/d
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name,folder,end in [('unobstructed_fixture_reference',BASE/'results/current_turn_wire1614/no_guide_control',None),('finiteGuide_precontact_only',BASE/'results/wire_local_mesh_pilot1655',.0025)]:
  root=ET.parse(folder/'scene.scn').getroot();radius=float(root.find('.//BeamInterpolation').get('radius'));rows=[]
  with (folder/'surface.csv').open() as f:
   for r in csv.DictReader(f):
    t=float(r['time_s'])
    if end is not None and t>end:break
    q=np.fromstring(r['q'],sep=' ').reshape(-1,16,3);centre=q.mean(1);k=curvature(centre);i=int(k.argmax());rows.append(dict(time_s=t,maximum_three_point_curvature_per_m=float(k[i]),station_index=i+1,centre_m=centre[i+1].tolist(),radius_times_curvature_proxy=float(radius*k[i])))
  peak=max(rows,key=lambda r:r['maximum_three_point_curvature_per_m']);native=[]
  with (folder/'states.csv').open() as f:
   for r in csv.DictReader(f):
    t=float(r['time_s'])
    if end is not None and t>end:break
    q=np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7);rot=Rotation.from_quat(q[:,3:]);angle=(rot[:-1].inv()*rot[1:]).magnitude();length=np.linalg.norm(np.diff(q[:,:3],axis=0),axis=1);assert np.all(length>0);native.append(float((angle/length).max()))
  result=dict(label=name,source_case=str(folder.relative_to(BASE/'results')),outputs=len(rows),accepted_time_limit_s=end,maximum_curvature_sample=peak,minimum_three_point_circle_radius_mm=1000/peak['maximum_three_point_curvature_per_m'] if peak['maximum_three_point_curvature_per_m'] else None,maximum_section_rotation_gradient_per_m=max(native),wire_radius_m=radius,configured_Young_modulus_Pa=float(root.find('.//BeamInterpolation').get('defaultYoungModulus')),configured_density_kg_m3=float(root.find('.//AdaptiveBeamForceFieldAndMass').get('massDensity')),material_allowable_strain='NOT MEASURED',material_minimum_bend_radius='NOT MEASURED',fatigue_life='NOT MEASURED',force_stroke_work='NOT MEASURED',input_sha256={f:sha(folder/f) for f in ('scene.scn','surface.csv','states.csv')});records.append(result);(out/(name+'_history.json')).write_text(json.dumps(rows))
 d=dict(status='ACTUAL_KINEMATIC_BEND_DEMAND_INVENTORY_ONLY',records=records,scope='Centre ofactual16point mappedsections andthreepointcircumcircle curvature;sectionrotationgradient alsoincludespotentialtorsion/shear,NOTNativeconstitutivestrain/stress/energy orstrengthlimit. r*kappa isGEOMETRICproxyonly,notverifiedmetal/strandedwirestrain. Unobstructed20mmfixturetrial isnotrealGuide/Cabletension/100ggrasp. ActualGuideinventoryrestrictedtoprecontact. No metricsfromfailedintersectingstates usedtoqualifyrealwire. ConfiguredE2GPa/rho1000researchassumptions,notmaterialselection. Actualmaterialdata requiredbefore bend/fatigue/Guide approval.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
