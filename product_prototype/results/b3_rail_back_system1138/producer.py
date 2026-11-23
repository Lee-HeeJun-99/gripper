"""Existing frozen observer + explicit Native linear system,checked for purity.
Adding a public system is a configuration intervention until q/v agree.
"""
import argparse,csv,json,subprocess,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/b3_rail_back_hold1129';tree=ET.parse(src/'scene.scn');root=tree.getroot();binary,source=compiled_observer('410')
    deps=subprocess.check_output(['ldd',str(binary)],text=True);assert not [x for x in deps.splitlines() if 'libSofa' in x and '=>' in x and '/home/ubuntu/SOFA/v26.06.00/' not in x]
    root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.LinearSystem'));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
    ET.SubElement(root,'MatrixLinearSystem',name='probeSystem',template='CompressedRowSparseMatrixd');root.find('SparseLDLSolver').set('linearSystem','@probeSystem')
    ET.SubElement(root,'NativeAssembledMatrixObserver',system='@probeSystem',filename=str(out/'assembled.csv'))
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    tree.write(out/'scene.scn');shutil.copy2(source,out/'Observer.cpp');(out/'ldd.txt').write_text(deps);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','5','--hideProgressBar',str(out/'scene.scn')]
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference_scene_sha256=sha(src/'scene.scn'),observer_binary_sha256=sha(binary),compiled_observer_source_sha256=sha(source),SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,estimated_runtime_s=1,child_limit_s=60,memory_GiB=4,purity_gate=1e-12)
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED')
    if proc['exit_code']==0 and '[ERROR]' not in logs and (out/'assembled.csv').exists():
        rows=list(csv.DictReader((out/'finger0.csv').open()));base=list(csv.DictReader((src/'finger0.csv').open()))[:5]
        err={f:max(float(abs(np.fromstring(x[f],sep=' ')-np.fromstring(y[f],sep=' ')).max()) for x,y in zip(rows,base)) for f in ('q_m','v_m_s','guide0_q_m','guide1_q_m')}
        matrix=list(csv.DictReader((out/'assembled.csv').open()));size=max(max(int(r['i']),int(r['j'])) for r in matrix)+1
        d.update(status='PASS_BOUNDED_ASSEMBLY_PATH_PURITY' if len(rows)==5 and max(err.values())<=1e-12 else 'FAIL_ASSEMBLY_PATH_PURITY',outputs=len(rows),state_errors=err,matrix_dimension=size,matrix_nonzero_entries=len(matrix),scope='First Native effective system matrix,NOT isolated mass or full nonlinear tangent')
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
