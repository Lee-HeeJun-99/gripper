"""Fresh prefix with read-only actual constraint system at worst saved wire gap."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_contact_policy1616';meta=json.loads((BASE/'results/window_contact_build1618/summary.json').read_text());binary=Path(meta['binary']);assert sha(binary)==meta['binary_sha256'];assert sha(BASE/'results/window_contact_build1618/Probe.cpp')==meta['compiled_source_sha256'];prior=json.loads((BASE/'results/min_turn_wire_assess1617/guide_history.json').read_text());worst=min(prior,key=lambda r:r['minimum_vertex_solid_gap_m']);target=worst['time_s'];root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));steps=round(target/dt);root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactGapProbe',body='@wire/dofs',solver='@unusedJournalSolver',filename=str(out/'probe'),startTime=str(target-dt-1e-12),endTime=str(target+1e-12))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'preflight.json').write_text(json.dumps(dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),observer_binary_sha256=sha(binary),observer_compiled_source_sha256=meta['compiled_source_sha256'],target_accepted_time_s=target,steps=steps,memory_GiB=4,child_limit_s=120,scope='ONLYread-onlyobserver/window addition,notphysical change or checkpointrestart. SameinitialScene andallbeam/Guidecollisionfeatures.'),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')],out/'process',120);error=0.;counts=[]
 for file,keys in [('states.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms')),('surface.csv',('q','v'))]:
  old=read(src/file)[:steps];new=read(out/file);counts.append(len(new));assert [r['time_s'] for r in old]==[r['time_s'] for r in new]
  for x,y in zip(old,new):
   for key in keys:error=max(error,float(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')).max()))
 logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));rows=read(out/'probe.rows.csv') if (out/'probe.rows.csv').exists() else [];ok=proc['exit_code']==0 and '[ERROR]'not in logs and counts==[steps]*2 and error<=1e-12 and any(r['phase']=='solve_end' for r in rows);d=dict(status='PASS_READONLY_WIRE_PHASE_PREFIX_ONLY' if ok else 'FAIL_OBSERVER_OR_NATIVE_PREFIX',process=proc,outputs=counts,maximum_observer_q_v_surface_impulse_error=error,target_accepted_time_s=target,observed_constraint_rows=len(rows),source_sha256=sha(Path(__file__)),scope='PurityandactualconstraintobservationONLY. W/dFree/impulse andgeometryresidualmustbeassessed independently;noneofthese repairpenetration orqualifygrasp.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
