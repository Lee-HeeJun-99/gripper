"""Full finite drive exact axial sweeps/gauges;nominal geometry,not actual assembly."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,cyl,union,transform,evaluate,sector,sha
from bridge_assembly_audit import hits

def axial_sweep(op,distance):
 M=np.eye(4)
 while op['op']=='transform':M=M@np.array(op['matrix']);op=op['shape']
 if op['op']!='union':raise ValueError('unsupported pin:do not substitute convexhull')
 if not np.allclose(M[:3,:3].T@M[:3,:3],np.eye(3),rtol=0,atol=1e-12) or np.linalg.det(M[:3,:3])<=0:raise ValueError('nonrigid pin transform')
 items=[]
 for q in op['items']:
  if q['op']!='cylinder':raise ValueError('unsupported swept component')
  z0,z1=q['z'];items.append(cyl(q['radius'],z0+min(distance,0),z1+max(distance,0),q['xy'],q['sections']))
 return transform(union(*items),M)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes'/a.candidate/'full_assembly_recipe.json';parts=json.loads(src.read_text())['parts'];shapes=[evaluate(p['shape']) for p in parts];pins=[];gauges=[];tools=[]
 for part in parts:
  group=part['group'];name=part['name']
  if not name.endswith('_headed_pin'):continue
  if group not in ('headed_pin_proxy','root_headed_pin_proxy','supplier_root_headed_pin_PROXY'):raise ValueError('unknown headed pin group;do not silently skip '+name)
  isroot='_root_headed_pin' in name;distance=10. if isroot else -10.;ownnut=name.replace('_headed_pin','_axle_nut');exclude=[name,ownnut];sweep=evaluate(axial_sweep(part['shape'],distance));pins.append(dict(pin=name,signed_axial_distance_mm=distance,full_swept_intersections=hits(sweep,parts,shapes,exclude)))
  if isroot:
   tool=evaluate(transform(cyl(1.,3.55,13.55),axial_sweep(part['shape'],distance)['matrix']));tools.append(dict(tool=name+'_outward_driver',intersections=hits(tool,parts,shapes,exclude)))
 expected={p['name'] for p in parts if p['name'].endswith('_headed_pin')}
 if not expected or {p['pin'] for p in pins}!=expected:raise ValueError('incomplete pin sweep coverage')
 for f,angle in enumerate((0,120,240)):
  S=sector(angle)
  for c,side in enumerate((1,-1)):
   for j,x in enumerate((44,52)):
    selected=[(p,s) for p,s in zip(parts,shapes) if p['name'] in ('palm_bridge_bores',f'f{f}_c{c}_root_mounted_bridge')]
    if len(selected)!=2:raise ValueError('actual Palm andintegralrootbridge required')
    gauge=evaluate(transform(cyl(1.65,1,20,(x,side*30)),S));gauges.append(dict(finger=f,cable=c,bolt=j,intersections=hits(gauge,[p for p,s in selected],[s for p,s in selected])))
    driver=evaluate(transform(cyl(2.25,21.2,46.2,(x,side*30)),S));tools.append(dict(tool=f'f{f}_c{c}_bolt{j}_driver',intersections=hits(driver,parts,shapes,[f'f{f}_c{c}_mount_bolt{j}'])))
 result=dict(status='COMPLETE_DRIVE_SERVICE_REVIEW_REQUIRED' if any(r['full_swept_intersections'] for r in pins) or any(r['intersections'] for r in gauges+tools) else 'NOMINAL_COMPLETE_DRIVE_GEOMETRY_CLEAR_NOT_PRODUCT_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,BASE/'cad/bridge_assembly_audit.py',BASE/'cad/manufacturing_assembly.py')},pins=pins,hole_gauges=gauges,tools=tools,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='24exact axial swept unions ofsteppedcylinders forfull10mm translation (18existing negativeaxis,6rootoutward). Looseownnutsremovedonlywherepresent.12actualPalm/rootbridgegaugebores,12mountdriver+6rootdriverpaths. No physicalthread/headslot/wrench/hand/preload/material/tolerance/capture or benchassemblyqualification. Allstaticpartobstaclesretained;notactuationCCD.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],blocked_pins=sum(bool(r['full_swept_intersections']) for r in pins),blocked_tools=sum(bool(r['intersections']) for r in tools),blocked_gauges=sum(bool(r['intersections']) for r in gauges),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
