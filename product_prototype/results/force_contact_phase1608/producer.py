"""Native penalty-force timing contrast,not a grasp solver replacement."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for spin in (0,10):
  src=BASE/f'results/spinning_normal_contract1606/Min_spin{spin}';d=out/f'spin{spin}';d.mkdir();root=ET.parse(src/'scene.scn').getroot();root.find('CollisionResponse').set('response','PenalityContactForceField');root.find('CollisionResponse').set('responseParams','')
  for n in root.iter():
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',str(d/'scene.scn')],d/'process',60);rows=list(csv.DictReader((d/'guide1.csv').open())) if (d/'guide1.csv').exists() else [];v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));error='[ERROR]'in logs;angular=float(abs(v[:,3:]-[spin,0,0]).max()) if len(v) else None;normal=float(abs(v[:,2]).max()) if len(v) else None;records.append(dict(initial_spin_rad_s=spin,process=proc,outputs=len(rows),SOFA_error=error,maximum_angular_velocity_change_rad_s=angular,maximum_normal_velocity_m_s=normal,status='PASS_SCOPE_NONZERO_NORMAL_RESPONSE_ZERO_SPIN_CHANGE' if proc['exit_code']==0 and not error and len(rows)==4 and normal>0 and angular<=1e-12 else 'FAIL_FORCE_CONTACT_PHASE_CONTRACT',scene_sha256=sha(d/'scene.scn')))
 result=dict(status='NATIVE_FORCE_RESPONSE_PHASE_COUPON_ONLY',records=records,scope='Onlystock contact RESPONSE changed frommu0LagrangeConstraint toNativePenaltyForce;FreeMotionODE/geometry/mass/initialstate preserved. Native default contact stiffness,not measuredmaterial. Nonzeroobjectnormalvelocity required,notzero-responsefakePASS. NoCable/FEM/Guide/grasp andnot justification to replacewholegraspcontact orclaimconvergence. NativeResponseRows impulsejournal doesNOTmeasure penaltyforce; onlyactualq/v usedhere.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
