"""One installed-intersector intervention;abort nonfinite states without corrections."""
import argparse,csv,json,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_finite_guard import finite_guard

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--velocity',type=float);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);template=BASE/'results/product_root_native_strict815/scene.scn';baseline=BASE/'results/product_root_native810/summary.json';meta=json.loads(baseline.read_text());tree=ET.parse(template);root=tree.getroot();root.find('LocalMinDistance').tag='MinProximityIntersection'
 if a.velocity is not None:root.find("./Node[@name='wheel']/MechanicalObject").set('velocity',f'0 0 {a.velocity} 0 0 0')
 for item in root.iter():
  if item.get('filename'):item.set('filename',str(out/Path(item.get('filename')).name))
 scene=out/'scene.scn';tree.write(scene);(out/'producer.py').write_bytes(Path(__file__).read_bytes());command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','80','--hideProgressBar',str(scene)]
 start=time.monotonic();proc=finite_guard(command,out/'process',420,state_file=out/'wheel.csv');failure=proc['nonfinite_observation'];rows=list(csv.DictReader((out/'wheel.csv').open())) if (out/'wheel.csv').exists() else [];finite=all(np.isfinite(np.fromstring(r['rigid_q']+' '+r['rigid_v'],sep=' ')).all() for r in rows);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));d={k:meta[k] for k in ('ASSUMED_mass_kg','ASSUMED_homogeneous_inertia_kg_m2','initial_velocity_m_s','dt_s','duration_s','binary_sha256','SDK')};d.update(status='INTERSECTOR_RUN_COMPLETED_NOT_QUALIFIED' if proc['exit_code']==0 and finite and len(rows)==80 and '[ERROR]' not in logs else 'FAIL_NATIVE_INTERSECTOR_PROBE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in (Path(__file__),template,baseline,BASE/'sofa/native_finite_guard.py',BASE.parent/'tools/film_guarded_process.py')},scene_sha256=sha(scene),command=command,process=proc,abort_observation=failure,all_states_finite=finite,state_rows=len(rows),runtime_s=time.monotonic()-start,scope='OnlyLocalMinDistance->MinProximityIntersection changed onstrict815initialscene,allfinitecollisionmodels/geometry/solverconstraintsretained. Newinitialstate,NOTresume. WatcherterminatesONLYitsownverifiedchildafteractualNaN,doesNOTchangeq/v/forces/logs/SDK/tolerances. No physics/time/energy/productPASS.',fabrication_ready=False)
 d['initial_velocity_m_s']=float(root.find("./Node[@name='wheel']/MechanicalObject").get('velocity').split()[2])
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:d[k] for k in ('status','state_rows','all_states_finite','abort_observation','runtime_s')},indent=2))
if __name__=='__main__':main()
