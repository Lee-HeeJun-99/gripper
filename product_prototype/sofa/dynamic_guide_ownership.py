"""Single collision-owner contrast in actual11BeamDOF wire; no physical changes."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
csv.field_size_limit(16*1024*1024)
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_local_mesh_pilot1655';root=ET.parse(src/'scene.scn').getroot();guide=root.find("Node[@name='finiteEyelet']");f=np.fromstring(guide.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);parts=[]
 for n in list(guide.findall('Node')):parts.extend(np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3).tolist());guide.remove(n)
 assert sorted(map(tuple,parts))==sorted(map(tuple,f));ET.SubElement(guide,'TriangleCollisionModel',moving='0',simulated='0',group='2');assert all(guide.find(k+'CollisionModel') is not None for k in ('Triangle','Line','Point'))
 for n in root.iter():
  for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'geometry.json').write_bytes((src/'geometry.json').read_bytes());(out/'preflight.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),change='ONLYGuideTriangle collisionownership32sectors->one exactorientedfacetunion. Same11BeamDOFs/local25umwiremesh/openendgeometry/ALLfeatures,E/rho/mass/BC/dt/mu0/tolerances. Notmechanicaldesignimprovement.',hypothesis='Static2x2showscap-onlyeffect0andGuideownershipchangesresponse. Testwhetherthatstaticobservation transfers toactualelasticwire atoriginal1655firstfacetfailure10.6ms;doNOTassumeitdoes.',steps=110,duration_s=.011,forecast_s=114,forecast_basis='actual1655 206.38s/200steps,110stepprefix~114s;420s hardcap',memory_GiB=4,child_limit_s=420,SDK='/home/ubuntu/SOFA/v26.06.00',binary_sha256={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},runSofa_sha256=sha(Path('/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00'))),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','110','--hideProgressBar',str(out/'scene.scn')],out/'process',420);rows=read(out/'states.csv') if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));old=read(src/'states.csv');error=0.;count=0
 for r,s in zip(old,rows):
  if float(r['time_s'])>.0025:break
  assert r['time_s']==s['time_s'];count+=1
  for key in ('rigid_q','rigid_v'):error=max(error,float(abs(np.fromstring(r[key],sep=' ')-np.fromstring(s[key],sep=' ')).max()))
 d=dict(status='NATIVE_DYNAMIC_OWNERSHIP_PREFIX_COMPLETED_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==110 else 'FAIL_NATIVE_OWNERSHIP_PREFIX',process=proc,outputs=len(rows),precontact_outputs=count,maximum_precontact_q_v_error=error,strict_precontact_API_pass=count==25 and error<=1e-12,source_sha256=sha(Path(__file__)),scope='NativeBeam dynamicprefix only;independentactualwholefacet/vertexassessment required. Not a repeatofstaticcoupon ororiginalfinepartitiontrial,notcontact/time/mesh/force/energy/grasp qualification. No state/physicscorrection orSDK edits.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
