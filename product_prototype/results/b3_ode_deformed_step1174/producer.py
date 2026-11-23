"""Frozen build + Native phase/matrix sampler;not a physics intervention."""
import argparse,csv,json,subprocess,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build',action='store_true');p.add_argument('--sample',type=float,default=.05);p.add_argument('--reference',choices=['b3_rail_back_hold1129','b3_rail_back_half1130','b3_ode_gravity_base1168'],default='b3_rail_back_hold1129');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    build=BASE/'cad/build_step_probe1142';binary=build/'libReGripStepProbe.so';code=BASE/'sofa/native_step_probe';(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    if a.build:
        for f in ('Probe.cpp','CMakeLists.txt'):shutil.copy2(code/f,out/f)
        original=sha(code/'Probe.cpp');proc=guarded(['cmake','--build',build,'-j','1'],out/'process',120);assert sha(code/'Probe.cpp')==original
        d=dict(status='BUILT_DIAGNOSTIC_ONLY' if proc['exit_code']==0 and binary.exists() else 'FAIL_BUILD',process=proc,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),compiled_source_sha256=original,binary=str(binary),binary_sha256=sha(binary) if binary.exists() else None,SDK='/home/ubuntu/SOFA/v26.06.00')
        if binary.exists():(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
        shutil.copy2(build/'CMakeCache.txt',out/'CMakeCache.txt')
    else:
        meta=json.loads((BASE/'results/b3_step_build1142/summary.json').read_text());assert sha(binary)==meta['binary_sha256'] and sha(BASE/'results/b3_step_build1142/Probe.cpp')==meta['compiled_source_sha256']
        deps=subprocess.check_output(['ldd',str(binary)],text=True);assert not [l for l in deps.splitlines() if 'libSofa' in l and '=>' in l and '/home/ubuntu/SOFA/v26.06.00/' not in l]
        src=BASE/'results'/a.reference;tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.LinearSystem'));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        ET.SubElement(root,'MatrixLinearSystem',name='stepSystem',template='CompressedRowSparseMatrixd');root.find('SparseLDLSolver').set('linearSystem','@stepSystem')
        ET.SubElement(root,'ReGripStepProbe',body='@finger0/dofs',freeBody='@free0/dofs',guides='@guides0/frames',elastic='@finger0/nativeFEM',solver='@constraints',system='@stepSystem',filename=str(out/'step'),sampleTime=str(a.sample))
        for n in root.iter():
            for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
        tree.write(out/'scene.scn');dt=float(root.get('dt'));steps=int(round(a.sample/dt))+4
        if not .0<a.sample<.9:raise ValueError('bounded valid source interval only')
        cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
        pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference=a.reference,reference_scene_sha256=sha(src/'scene.scn'),binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'],SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,dt_s=dt,sample_end_s=a.sample,expected_outputs=steps,estimated_runtime_s=5,child_limit_s=120,memory_GiB=4,state_purity_gate=1e-12)
        (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED')
        if proc['exit_code']==0 and '[ERROR]' not in logs and (out/'step.A.csv').exists():
            rows=list(csv.DictReader((out/'finger0.csv').open()));base=list(csv.DictReader((src/'finger0.csv').open()))[:steps]
            error={f:max(float(abs(np.fromstring(x[f],sep=' ')-np.fromstring(y[f],sep=' ')).max()) for x,y in zip(rows,base)) for f in ('q_m','v_m_s','guide0_q_m','guide1_q_m')}
            phases=list(csv.DictReader((out/'step.phases.csv').open()));d.update(status='PASS_BOUNDED_STEP_OBSERVER_PURITY' if len(rows)==steps and max(error.values())<=1e-12 else 'FAIL_STEP_OBSERVER_PURITY',outputs=len(rows),state_errors=error,phases=[r['phase'] for r in phases],phase_clocks_s=[float(r['time_s']) for r in phases],scope='Sampled actualNativeAandpreviousacceptedstate;notfullphysicsqualification')
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
