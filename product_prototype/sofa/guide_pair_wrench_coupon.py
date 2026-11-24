"""Reuse frozen read-only NativePairRows for actual mapped Guide contact wrenches."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows
def read(p):return list(csv.DictReader(p.open()))
def main():
 checked_binary,compiled_source=compiled_pair_rows()
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/unbraced_three1544';root=ET.parse(src/'scene.scn').getroot();meta=json.loads((BASE/'results/b3_direct_rows514/summary.json').read_text());binary=Path(meta['row_binary_path']);assert sha(binary)==meta['row_binary_sha256'];root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
 for i in range(3):ET.SubElement(root,'NativePairRows',body=f'@guides{i}/frames',solver='@constraints',filename=str(out/f'direct{i}.csv'))
 # Resolve the actual MechanicalObject name, not a guessed component API.
 for i,n in enumerate(root.findall('NativePairRows')):
  state=root.find(f"Node[@name='guides{i}']/MechanicalObject");n.set('body',f"@guides{i}/{state.get('name')}")
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),observer_binary_sha256=sha(binary),observer_source_sha256=sha(BASE/'sofa/native_pair_rows/Observer.cpp'),SDK='/home/ubuntu/SOFA/v26.06.00',child_limit_s=420,memory_GiB=4,duration_s=.6,scope='Read-onlyobserver addition ONLY,actualq/vpurity required;NOphysicsmodification ornewHoldingclaim');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')],out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));purity=0.;outputs=[]
 for file,keys in [('object.csv',['rigid_q','rigid_v'])]+[(f'finger{i}.csv',['q_m','v_m_s']) for i in range(3)]+[(f'guide_frames{i}.csv',['rigid_q','rigid_v']) for i in range(3)]:
  old=read(src/file);new=read(out/file);assert [float(r['time_s']) for r in old]==[float(r['time_s']) for r in new];outputs.append(len(new))
  for x,y in zip(old,new):
   for k in keys:purity=max(purity,float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()))
 pairs={}
 for r in read(out/'response_rows.csv'):
  names=[r['model0'],r['model1']]
  if all('/guides'in s for s in names) and names[0].split('/')[1]!=names[1].split('/')[1]:pairs[(float(r['time_s']),int(r['row_id']))]=names
 records=[]
 for i in range(3):
  for r in read(out/f'direct{i}.csv'):
   key=(float(r['time_s']),int(r['row_id']))
   if key not in pairs:continue
   impulse=np.fromstring(r['J'],sep=' ')*float(r['lambda_Ns']);records.append(dict(time_s=key[0],row_id=key[1],guide_finger=i,rigid_column=int(r['column_id']),source_pair=' | '.join(pairs[key]),impulse_Ns_Nms=impulse.tolist()))
 (out/'pair_wrenches.json').write_text(json.dumps(records));d=dict(status='PASS_READONLY_GUIDE_ROW_WRENCH_COUPON' if process['exit_code']==0 and '[ERROR]'not in logs and outputs==[240]*7 and purity<=1e-12 and len(records)>0 else 'FAIL_OBSERVER_OR_PROVENANCE',process=process,outputs=outputs,maximum_observer_q_v_error=purity,actual_source_resolved_rows=len(records),maximum_single_row_linear_force_N=max([float(np.linalg.norm(r['impulse_Ns_Nms'][:3]))/.0025 for r in records],default=None),maximum_single_row_moment_Nm=max([float(np.linalg.norm(r['impulse_Ns_Nms'][3:]))/.0025 for r in records],default=None),scope='Actual mappedparentRigid3Jtransposelambda/dt,source-resolvedrowforce/moment atNativeparentreferencepoint;NOTfullcontactsum,unprojectedattachmentreaction,wholeenergy orHolding qualification',raw_hashes={f.name:sha(f) for f in out.glob('*.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
