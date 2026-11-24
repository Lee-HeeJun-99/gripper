"""Frozen read-only observer on completed proximal-terminal trajectory."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_proximal_terminal1328'
 meta=json.loads((BASE/'results/contact_provenance_build1242/summary.json').read_text());binary=BASE/'cad/contact_provenance_build1242/libReGripContactProvenance.so';assert sha(binary)==meta['binary_sha256'];assert sha(BASE/'results/contact_provenance_build1242/Observer.cpp')==meta['compiled_source_sha256']
 baseline=json.loads((src/'summary.json').read_text());assert baseline['status']=='BOUNDED_EXECUTION_ONLY';forecast=baseline['process']['runtime_s']*1.5;assert forecast<180
 tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(root,'ReGripContactProvenance',narrow=root.find('NativeDetectionPairs').get('narrow'),filename=str(out/'provenance'),startTime='1.1949',endTime='1.1976')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn')
 for f in ('mesh.json','config.json'):(out/f).write_bytes((src/f).read_bytes())
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','480','--hideProgressBar',str(out/'scene.scn')]
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),observer_binary_sha256=sha(binary),observer_source_sha256=meta['compiled_source_sha256'],forecast_s=forecast,child_limit_s=180,memory_GiB=4,previous_time_window_s=[1.1949,1.1976],scope='Read-only material provenance;not new actuation or convergence')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',180);equal={}
 for f in ('object.csv','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv','constraints.csv','support.csv'):
  actual=list(csv.DictReader((out/f).open()));base=list(csv.DictReader((src/f).open()));equal[f]=len(actual)==480 and actual==base
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts={f:len(list(csv.DictReader((out/f).open()))) for f in ('provenance.features.csv','provenance.children.csv')}
 result=dict(status='PASS_READ_ONLY_PREFIX' if proc['exit_code']==0 and '[ERROR]'not in logs and all(equal.values()) and min(counts.values())>0 else 'FAIL_EXECUTION_OR_PURITY',process=proc,exact_record_equality=equal,counts=counts,physical_validation='NOT QUALIFIED')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
