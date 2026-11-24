"""Fresh Native finite-hardware exploration after separated/loaded cyclic coupons.
Only collision-facet cyclic starts change;FEM tet ordering and all physics retained.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from cyclic_projection_contract import canonicalize
from finite_hardware_grasp_pilot import run_three
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.6,1.2,2.),default=.6);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/finite_hardware_new1569';root=ET.parse(src/'scene.scn').getroot();probe=BASE/'results/cyclic_projection_contract1572';assert json.loads((probe/'summary.json').read_text())['status']=='PASS_SEPARATED_AND_LOADED_NATIVE_CYCLIC_COUPONS_ONLY';assert root.find('NewProximityIntersection') is not None;assert root.find("Node[@name='object']/Node/MechanicalObject").get('template')=='Rigid3d';changes=canonicalize(root);forecast=120.
 if a.duration>.6:
  assert a.pilot;prior=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());intervention=json.loads((BASE/'results'/a.pilot/'intervention.json').read_text());assert prior['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and intervention['source_scene_sha256']==sha(src/'scene.scn');forecast=prior['process']['runtime_s']*a.duration/prior['duration_s']*2;assert forecast<420
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 meta=json.loads((src/'preflight.json').read_text());(out/'intervention.json').write_text(json.dumps(dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),coupon_sha256=sha(probe/'summary.json'),canonicalizer_sha256=sha(BASE/'sofa/cyclic_projection_contract.py'),projection_reference_sha256=sha(BASE/'sofa/new_projection_audit.py'),changes=changes,only_change='Cyclicstartvertex ofcollisionfacets ONLY;sameunorderedtriangles/orientation/positions/FEMtetordering/material/mass/inertia/SphereRigid3/constraints/cableinputs/friction/buffers/solver/NativeNewProximity. ALLfiniteEyeletANDSupportcollisionsenabled.',scope='InstalledNewprojectionbranch orderingworkaroundcandidate;NOTSDKpatch ornewsolver. Samephysicalgeometry butcontactfeatureIDs maychange. Allsavedfacetangles andactualgap/response/hardwarebracing requireaudit;oldtime/meshFAILremain.',forecast_s=forecast),indent=2));run_three(root,out,src,meta['eyelet'],meta['parts'],round(a.duration/.0025),a.duration,forecast);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'canonicalizer.py').write_bytes((BASE/'sofa/cyclic_projection_contract.py').read_bytes());(out/'projection_reference.py').write_bytes((BASE/'sofa/new_projection_audit.py').read_bytes())
if __name__=='__main__':main()
