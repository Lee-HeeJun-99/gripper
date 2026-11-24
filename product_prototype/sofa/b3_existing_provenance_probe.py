"""Reuse frozen1242 observer on B3;no rebuild or custom solver."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--late',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';meta=json.loads((BASE/'results/contact_provenance_build1242/summary.json').read_text());binary=BASE/'cad/contact_provenance_build1242/libReGripContactProvenance.so';assert sha(binary)==meta['binary_sha256'];assert sha(BASE/'results/contact_provenance_build1242/Observer.cpp')==meta['compiled_source_sha256'];deps=subprocess.check_output(['ldd',str(binary)],text=True);assert not [s for s in deps.splitlines() if 'libSofa'in s and '=>'in s and '/home/ubuntu/SOFA/v26.06.00/'not in s];(out/'ldd.txt').write_text(deps);tree=ET.parse(src/'scene.scn');root=tree.getroot();narrow_link=root.find('NativeDetectionPairs').get('narrow');assert root.find(f"BVHNarrowPhase[@name='{narrow_link[1:]}']")is not None;root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));window=[1.4249,1.4298] if a.late else [1.0949,1.0998];ET.SubElement(root,'ReGripContactProvenance',narrow=narrow_link,filename=str(out/'provenance'),startTime=str(window[0]),endTime=str(window[1]))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());steps=574 if a.late else 442;limit=180 if a.late else 120;cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];pr=json.loads((src/'summary.json').read_text());forecast=pr['process']['runtime_s']*(steps/800)*1.5;assert forecast<=limit;pre=dict(command=cmd,scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),observer_binary_sha256=sha(binary),observer_compiled_source_sha256=meta['compiled_source_sha256'],estimated_runtime_s=forecast,child_limit_s=limit,memory_GiB=4,SDK='/home/ubuntu/SOFA/v26.06.00',window_previous_time_s=window,physical_validation='NOT QUALIFIED');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',limit);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));errors={};counts={};exact={}
 for file in ('object.csv','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv','constraints.csv','support.csv'):
  rr=list(csv.DictReader((out/file).open())) if (out/file).exists() else [];base=list(csv.DictReader((src/file).open()))[:steps];counts[file]=len(rr);exact[file]=rr==base;error=0.
  for r,b in zip(rr,base):
   for key in r:
    try:x=np.array([float(v) for v in r[key].split()]);y=np.array([float(v) for v in b[key].split()])
    except ValueError:continue
    assert x.shape==y.shape and np.isfinite(x).all() and np.isfinite(y).all()
    if len(x):error=max(error,float(abs(x-y).max()))
  errors[file]=error
 features=out/'provenance.features.csv';children=out/'provenance.children.csv';nf=len(list(csv.DictReader(features.open()))) if features.exists() else 0;nc=len(list(csv.DictReader(children.open()))) if children.exists() else 0;clean=proc['exit_code']==0 and '[ERROR]'not in logs and all(v==steps for v in counts.values()) and max(errors.values(),default=1)<=1e-12 and all(exact.values()) and nf>0 and nc>0;d=dict(status='PASS_BOUNDED_READ_ONLY_B3_PROVENANCE' if clean else 'FAIL_EXECUTION_PURITY_OR_EMPTY_DATA',process=proc,outputs=counts,max_numeric_errors=errors,all_record_fields_exact=exact,detector_features=nf,child_J_entries=nc,physical_validation='NOT QUALIFIED',scope='Same-dt read-only observer prefix purity only. Window journal previous time is not accepted endtime;join explicit clock before forces. Not a newgrasp or numerical convergence.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
