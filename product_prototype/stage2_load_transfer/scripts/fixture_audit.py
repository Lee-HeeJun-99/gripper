"""Independent actual STEP/STL and maximum finished-end fit audit."""
import argparse,json,sys
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage1_manufacturing/scripts'))
from incremental_stage1 import read,sha,volume,common,cyl,translate
from OCP.BRepCheck import BRepCheck_Analyzer
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'hardware_test/fixtures/split_end2';out=ROOT/'hardware_test/inspection'/a.tag;out.mkdir(parents=True,exist_ok=False)
    summary=json.loads((source/'summary.json').read_text());rows=[];parts={}
    for part in summary['parts']:
        path=source/part['STEP'];assert sha(path)==part['STEP_SHA256'];s=read(path);parts[part['ID']]=s
        mesh=trimesh.load(source/part['STL'],force='mesh')
        err=abs(mesh.volume/volume(s)-1)
        rows.append(dict(part=part['ID'],BRep_valid=BRepCheck_Analyzer(s).IsValid(),watertight=bool(mesh.is_watertight),positive_mesh=bool(mesh.is_volume),mesh_volume_relative_error=err))
    # Three maximum envelope portions meet on shared faces, not overlapping
    # volumes. Test each separately; don't require a fictitious fused swage.
    ends=[cyl(1.9,(0,0,3),3),cyl(1.4,(0,0,0),3),cyl(.26,(0,0,-3),3)]
    contacts=[]
    for distance in np.linspace(5,0,21):
        for label,sign in [('GRIP_L',-1),('GRIP_R',1)]:
            moved=translate(parts[label],sign*distance,0,0)
            contacts.append(dict(opening_mm=float(distance),part=label,common_mm3=max(common(moved,end) for end in ends)))
    passed=all(x['BRep_valid'] and x['watertight'] and x['positive_mesh'] and x['mesh_volume_relative_error']<.01 for x in rows) and all(x['common_mm3']<1e-8 for x in contacts)
    result=dict(status='PASS' if passed else 'FAIL',scope='FIXTURE GEOMETRY/FINITE MAX-END LOADING PATH SAMPLES ONLY',
        parts=rows,maximum_end_samples=contacts,source_SHA256=sha(Path(__file__)),input_SHA256=sha(source/'summary.json'),
        hardware_tested=False,proof_load_qualified=False,command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/fixture_audit.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='maximum_end_samples'},indent=2))
if __name__=='__main__':main()
