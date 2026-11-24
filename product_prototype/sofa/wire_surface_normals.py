"""Native per-step point normals for Local finite-wire surface collision."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/current_turn_wire1614/guide';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();changed=[]
 for n in root.iter('PointCollisionModel'):
  assert n.get('computeNormals') in (None,'0','false');n.set('computeNormals','1');changed.append(n.attrib.copy())
 assert len(changed)==2
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'preflight.json').write_text(json.dumps(dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),change='ONLYactualNativePointCollisionModelcomputeNormals enabledonwireandfixedEyelet. ALLcollisionmodels/geometry/BC/material/dt/buffers/friction/tolerance retained.',SDK_PointCollisionModel_inl_sha256=sha(Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Collision.Geometry/sofa/component/collision/geometry/PointCollisionModel.inl')),hypothesis='Localgeometryconetestneeds currentmeshvertexnormals;defaultfalsecouldfiltercurvedAdaptiveBeamSurface contacts. ThisisnotearlierRigidSpheremissingdispatchcase.',memory_GiB=4,child_limit_s=120),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1200','--hideProgressBar',str(out/'scene.scn')],out/'process',120);rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));d=dict(status='NATIVE_NORMALS_COUPON_COMPLETED_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==1200 else 'FAIL_NATIVE_NORMALS_COUPON',process=proc,outputs=len(rows),scope='ActualNative normals capability only until independentfinitegap/source assessment. NoSphereinthiscoupon,not1563repeat. No newphysics solver orSDK changes.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
