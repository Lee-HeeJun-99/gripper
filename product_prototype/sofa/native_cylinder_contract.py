"""Installed primitive contact capability,not an assumed replacement for finite mesh."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_direct_rows514/1';records=[]
 for kind in ('Sphere','Cylinder'):
  d=out/kind;d.mkdir();root=ET.parse(src/'scene.scn').getroot()
  for i in (0,1):
   n=root.find(f"Node[@name='guide{i}']");q=f'{i*.0029} 0 0 0 0 0 1';n.find('MechanicalObject').set('position',q);n.find('MechanicalObject').set('velocity','0 0 0 0 0 0');col=n.find("Node[@name='collision']")
   if kind=='Cylinder':
    n.remove(col);ET.SubElement(n,'CylinderCollisionModel',template='Rigid3d',defaultRadius='.0015',defaultHeight='.002',defaultLocalAxis='0 1 0',group=str(i+1))
   else:col.find('MechanicalObject').set('position',f'{i*.0029} 0 0');col.find('SphereCollisionModel').set('radius','.0015')
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','8','--hideProgressBar',str(d/'scene.scn')],d/'process',60);logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));response=list(csv.DictReader((d/'response0.csv').open())) if (d/'response0.csv').exists() else [];nonzero=sum(float(r['lambda_Ns'])!=0 for r in response);records.append(dict(primitive=kind,process=process,ERROR='[ERROR]'in logs,nonzero_actual_response_rows=nonzero,scene_sha256=sha(d/'scene.scn'),status='ACTUAL_NATIVE_PRIMITIVE_RESPONSE_OBSERVED' if process['exit_code']==0 and '[ERROR]'not in logs and nonzero else 'BLOCKED_NATIVE_PRIMITIVE_CONTACT_PATH'))
 summary=dict(status='INSTALLED_PRIMITIVE_CAPABILITY_COUPON_ONLY',records=records,scope='Two free prescribedINITIALrigids,zeroexternalforce,deliberate0.1mminitialoverlap ONLYforcomponentresponsecapability,NOTgraspinitialcondition/physicalcontactvalidation. Cylinderfactorypresence alone insufficient;actualnonzerorowsrequired. Spherecontrolcalibratespipeline. NoSDK/solverchange.',source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'));(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
