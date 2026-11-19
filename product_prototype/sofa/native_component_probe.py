"""Execute installed primary bending examples as AVAILABILITY probes, not FEM gates."""
import argparse,json,subprocess
from pathlib import Path
from native_bending_coupon import BASE,ROOT,sha,guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    sdk=Path('/home/ubuntu/SOFA/v26.06.00');records=[]
    for model in ('TriangleBendingSprings','TriangularBendingSprings','FastTriangularBendingSprings'):
        scene=sdk/'share/sofa/examples/Component/SolidMechanics/Spring'/f'{model}.scn'
        d=out/model;d.mkdir()
        if not scene.exists():
            records.append(dict(model=model,status='NOT_AVAILABLE_EXAMPLE'));continue
        (d/'installed_example.scn').write_bytes(scene.read_bytes())
        process=guarded([sdk/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',scene],d/'process',480)
        logs=''.join((d/'process'/x).read_text() for x in ('stdout.log','stderr.log'))
        records.append(dict(model=model,source_scene=str(scene),scene_sha256=sha(scene),process=process,
                            status='AVAILABLE_EXAMPLE_EXECUTED_ONLY' if process['exit_code']==0 and '[ERROR]' not in logs and '2 iterations done' in logs else 'FAIL_EXAMPLE_PROBE'))
    data=dict(scope='Factory/example execution only,NOT shell constitutive calibration,bending convergence or B3 certification',
              sdk=str(sdk),source_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

if __name__=='__main__':main()
