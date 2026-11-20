"""Geometry-only component COM/normalized inertia vs actual public Native mass.
No material density,union mass or physical calibration is invented.
"""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
sys.path.insert(0,str(BASE/'cad'))
from finite_guide_product import support
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_alarm_window485';cfg=json.loads((src/'config.json').read_text());tree=ET.parse(src/'scene.scn');cad=BASE/'meshes/finite_eyelet_support_v11';design=json.loads((cad/'geometry.json').read_text());ring,_=eyelet(cfg,64);records=[]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  qrest=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);actual=json.loads((src/f'guide_frames{f}.csv.mass.json').read_text())['elements']
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    idx=cable*6+k;frame=qrest[idx];R=rotation(frame[3:]);guide=next(g for g in design['guides'] if g['finger']==f and g['cable']==cable and g['station_mm']==x);eye=trimesh.Trimesh(ring.vertices@np.array(guide['basis']).T+guide['center_mm'],ring.faces,process=False);bracket=support(cfg,x,side,angle);M=np.array(actual[idx]['matrix']);mass=actual[idx]['mass_kg'];component=[]
    for label,mesh in [('eyelet',eye),('support',bracket)]:
     # Translation/rotation into the Native body frame before volume moments.
     local=(mesh.vertices-frame[:3]*1000)@R;part=trimesh.Trimesh(local,mesh.faces,process=False);props=part.mass_properties
     if props.volume<=0 or not part.is_watertight:raise ValueError('undefined component mass properties')
     com=np.array(props.center_mass);I_com=np.array(props.inertia)/props.mass;I_frame=(I_com+(com@com)*np.eye(3)-np.outer(com,com))*1e-6;component.append(dict(part=label,volume_mm3=float(props.volume),uniform_density_component_COM_body_m=(com*.001).tolist(),component_COM_offset_norm_mm=float(np.linalg.norm(com)),component_normalized_inertia_at_COM_m2=(I_com*1e-6).tolist(),component_normalized_inertia_about_Native_origin_m2=I_frame.tolist(),physical_density_kg_m3=None,physical_component_mass_kg=None))
    records.append(dict(finger=f,cable=cable,station_mm=x,actual_Native_assumed_mass_kg=mass,actual_Native_rotational_inertia_per_mass_m2=(M[3:,3:]/mass).tolist(),actual_Native_mass_has_translation_rotation_cross_block=bool(np.any(M[:3,3:]!=0)),components=component,union_COM=None,union_inertia=None))
 result=dict(status='GEOMETRIC_COMPONENT_MASS_AUDIT_NOT_PHYSICAL_CALIBRATION',scope='Partwise constant-density NORMALIZED geometric moments only;densities and joint/overlap unknown. Actual Native mass is a public research lump at its frame origin. No support-eyelet union sum/double counting,no selected physical inertia,no Native model change. A future COM/inertia revision is a PHYSICAL model candidate,not a numerical convergence fix.',source_sha256=sha(Path(__file__)),source_config_sha256=sha(src/'config.json'),source_CAD_sha256=sha(cad/'geometry.json'),records=records,eyelet_COM_offset_range_mm=[min(c['component_COM_offset_norm_mm'] for r in records for c in r['components'] if c['part']=='eyelet'),max(c['component_COM_offset_norm_mm'] for r in records for c in r['components'] if c['part']=='eyelet')],support_COM_offset_range_mm=[min(c['component_COM_offset_norm_mm'] for r in records for c in r['components'] if c['part']=='support'),max(c['component_COM_offset_norm_mm'] for r in records for c in r['components'] if c['part']=='support')],actual_material_density='NOT MEASURED',physical_mass_qualification='BLOCKED_UNSELECTED_MATERIAL_AND_JOIN')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
