"""Build/run read-only Native tangent probe with full saved-prefix purity check."""
import argparse,csv,json,subprocess,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');p.add_argument('--sample',type=float,default=.1);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);build=BASE/'cad/build_deformed_probe1120';binary=build/'libReGripDeformedProbe.so';source=BASE/'sofa/native_deformed_probe'
    shutil.copy2(Path(__file__),out/'producer.py')
    if a.build:
        for f in ('Probe.cpp','CMakeLists.txt'):shutil.copy2(source/f,out/f)
        before=sha(source/'Probe.cpp');proc=guarded(['cmake','--build',build,'-j','1'],out/'process',120)
        assert before==sha(source/'Probe.cpp')
        d=dict(status='BUILT_DIAGNOSTIC_ONLY' if proc['exit_code']==0 and binary.exists() else 'FAIL_BUILD',process=proc,binary=str(binary),binary_sha256=sha(binary) if binary.exists() else None,compiled_source_sha256=before,SDK='/home/ubuntu/SOFA/v26.06.00',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
        if binary.exists():(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
        shutil.copy2(build/'CMakeCache.txt',out/'CMakeCache.txt')
    else:
        meta=json.loads((BASE/'results/b3_deformed_build1120/summary.json').read_text());assert sha(binary)==meta['binary_sha256'] and sha(BASE/'results/b3_deformed_build1120/Probe.cpp')==meta['compiled_source_sha256']
        src=BASE/'results/b3_high_force_isolation1105';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        ET.SubElement(root.find("./Node[@name='finger0']"),'ReGripDeformedProbe',body='@dofs',elastic='@nativeFEM',filename=str(out/'probe'),sampleTime=str(a.sample))
        for n in root.iter():
            for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
        tree.write(out/'scene.scn');steps=int(round(a.sample/.0025))+4
        cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
        pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],reference_scene_sha256=sha(src/'scene.scn'),command=cmd,SDK='/home/ubuntu/SOFA/v26.06.00',expected_outputs=steps,sample_s=a.sample,estimated_runtime_s=3,child_limit_s=120,memory_GiB=4,position_velocity_purity_gate=1e-12,force_tangent_relative_gate=.001)
        (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120)
        logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED')
        if proc['exit_code']==0 and '[ERROR]' not in logs and (out/'probe.fd.csv').exists():
            rows=list(csv.DictReader((out/'finger0.csv').open()));base=list(csv.DictReader((src/'finger0.csv').open()))[:steps]
            error={f:max(float(abs(np.fromstring(x[f],sep=' ')-np.fromstring(y[f],sep=' ')).max()) for x,y in zip(rows,base)) for f in ('q_m','v_m_s','guide0_q_m','guide1_q_m')}
            fd=list(csv.DictReader((out/'probe.fd.csv').open()));relative=[float(r['error_N_per_m'])/float(r['fd_norm_N_per_m']) for r in fd]
            d.update(status='PASS_BOUNDED_OBSERVER_PURITY' if len(rows)==steps and max(error.values())<=1e-12 else 'FAIL_OBSERVER_PURITY',outputs=len(rows),state_errors=error,tangent_fd_relative_errors=relative,tangent_status='PASS_SINGLE_DIRECTION_ONLY' if max(relative)<=.001 else 'FAIL_SINGLE_DIRECTION_TANGENT',sample_time_s=float(fd[0]['time_s']),scope='One accepted state/direction only;not full mapped tangent/time/grasp qualification')
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
