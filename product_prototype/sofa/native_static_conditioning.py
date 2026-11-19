"""Coordinate/consistent-unit contrasts of archived372, with unchanged force gate.
Does not modify archived scenes or turn failed Newton states into accepted evidence.
"""
import argparse,json
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=BASE/'results'/args.tag;out.mkdir(exist_ok=False);records=[]
    source=BASE/'results/native_static_bending372/21/scene.scn'
    for label,scale in [('translated_SI',1.),('translated_mm_N',1000.)]:
        d=out/label;d.mkdir();tree=ET.parse(source);root=tree.getroot()
        for element in root.iter():
            if element.tag in ('MechanicalObject','MeshTopology'):
                q=np.fromstring(element.get('position'),sep=' ').reshape(-1,3)
                q[:,0]-=.05
                element.set('position',flat(q*scale))
            if element.tag=='TetrahedronFEMForceField':
                element.set('youngModulus',str(float(element.get('youngModulus'))/scale**2))
            if element.tag=='NativePointJournal':element.set('filename',str(d/'states.csv'))
        tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/name).read_text() for name in ('stdout.log','stderr.log'))
        records.append(dict(contrast=label,process=process,scene_sha256=sha(d/'scene.scn'),
                            status='FAIL_NATIVE_SOLVE' if process['exit_code']!=0 or '[ERROR]' in logs or 'Line search failed' in logs else 'COMPLETED_DIAGNOSTIC_ONLY'))
    (out/'producer.py').write_bytes(__import__('pathlib').Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(dict(source_scene_sha256=sha(source),force_gate_N=1e-12,
        scope='Static coordinate/unit arithmetic contrasts,not B3 physics qualification',records=records),indent=2))
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
