"""One-step input knockout using existing force owner;no state manipulation."""
import argparse,csv,json,subprocess,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);build=BASE/'cad/build_cable_pause1148';binary=build/'libReGripCablePause.so';code=BASE/'sofa/native_cable_pause';(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    if a.build:
        for f in ('Pause.cpp','CMakeLists.txt'):shutil.copy2(code/f,out/f)
        h=sha(code/'Pause.cpp');proc=guarded(['cmake','--build',build,'-j','1'],out/'process',120);assert h==sha(code/'Pause.cpp')
        d=dict(status='BUILT_INPUT_CONTRAST_ONLY' if proc['exit_code']==0 and binary.exists() else 'FAIL_BUILD',process=proc,binary=str(binary),binary_sha256=sha(binary) if binary.exists() else None,compiled_source_sha256=h,SDK='/home/ubuntu/SOFA/v26.06.00',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        if binary.exists():(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
        shutil.copy2(build/'CMakeCache.txt',out/'CMakeCache.txt')
    else:
        meta=json.loads((BASE/'results/b3_pause_build1148/summary.json').read_text());assert sha(binary)==meta['binary_sha256'] and sha(BASE/'results/b3_pause_build1148/Pause.cpp')==meta['compiled_source_sha256']
        src=BASE/'results/b3_step_base1143';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));seq=root.find("./Node[@name='finger0']/NativeCableSequence");seq.set('name','inputSequence')
        ET.SubElement(root,'ReGripCablePause',target='@finger0/inputSequence',endTime='.05',filename=str(out/'pause.csv'))
        for n in root.iter():
            for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
        tree.write(out/'scene.scn');cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','24','--hideProgressBar',str(out/'scene.scn')]
        pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference_scene_sha256=sha(src/'scene.scn'),command=cmd,SDK='/home/ubuntu/SOFA/v26.06.00',binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],change='ONE step ending50ms maximumForceN0;rest2.5N C2 unchanged. Explicit NEW INPUT,not observer purity.',expected_outputs=24,estimated_runtime_s=1,child_limit_s=60,memory_GiB=4)
        (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else []
        d=dict(status='COMPLETED_DECLARED_INPUT_CONTRAST' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==24 else 'FAIL_INPUT_CONTRAST_EXECUTION',process=proc,outputs=len(rows),physical_validation='NOT QUALIFIED',holding='NOT RUN',scope='Input knockout diagnostic,not performance or observer-purity PASS')
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
