"""Read-only actual candidate BRep/STL and independent adaptive integral audit."""
import argparse,json,sys,shutil
from pathlib import Path
import numpy as np
import trimesh
from baseline_registry import ROOT,S2,REPO,ref,dump,sha
sys.path.insert(0,str(S2/'scripts'))
from extract_geometry import load,properties
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'cad/exports'/a.candidate/'summary.json';case=json.loads(source.read_text())
    out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    records=[];checks=[]
    for name,r in case['part_references'].items():
        path=REPO/r['path'];assert sha(path)==r['SHA256'];s=load(path);v,c,j=properties(s)
        records.append(dict(part_ID=name,volume_m3=v,centroid_m=c.tolist(),central_geometric_inertia_m5=j.tolist(),STEP=r))
    total=sum(r['volume_m3'] for r in records);centre=sum(r['volume_m3']*np.array(r['centroid_m']) for r in records)/total;inertia=np.zeros((3,3))
    for r in records:
        d=np.array(r['centroid_m'])-centre;inertia+=np.array(r['central_geometric_inertia_m5'])+r['volume_m3']*(d@d*np.eye(3)-np.outer(d,d))
    av,ac,ai=properties(load(REPO/case['assembly']['path']))
    errors=dict(volume_relative=abs(av-total)/total,centroid_m=float(np.linalg.norm(ac-centre)),inertia_relative=float(np.linalg.norm(ai-inertia)/np.linalg.norm(ai)))
    changed=case.get('changed')
    if changed is None:
        changed=[dict(part_ID=n,STEP=case['part_references'][n],STL=ref((REPO/case['part_references'][n]['path']).with_suffix('.stl'))) for n in case['changed_parts']]
    for row in changed:
        s=load(REPO/row['STEP']['path']);v,c,j=properties(s);e=TopExp_Explorer(s,TopAbs_SOLID);n=0
        while e.More():n+=1;e.Next()
        mesh=trimesh.load(REPO/row['STL']['path'],force='mesh');err=abs(mesh.volume*1e-9/v-1)
        checks.append(dict(part_ID=row['part_ID'],BRep_valid=BRepCheck_Analyzer(s).IsValid(),solid_count=n,positive_volume=v>0,STL_closed=bool(mesh.is_watertight),STL_positive=bool(mesh.is_volume),STL_volume_relative=err))
    ok=errors['volume_relative']<1e-8 and errors['centroid_m']<1e-9 and errors['inertia_relative']<1e-8 and all(r['BRep_valid'] and r['solid_count']==1 and r['positive_volume'] and r['STL_closed'] and r['STL_positive'] and r['STL_volume_relative']<.01 for r in checks)
    dump(out/'parts.json',records)
    result=dict(status='PASS' if ok else 'FAIL',scope='ADAPTIVE GEOMETRIC INTEGRALS / CHANGED BREP/STL ONLY',candidate=ref(source),assembly=case['assembly'],errors=errors,changed_part_checks=checks,parts=ref(out/'parts.json'),producer=ref(out/'producer.py'),integral_implementation=ref(S2/'scripts/extract_geometry.py'),old_failure_preserved=True,physical_mass_qualified=False,stage1_release=False,stage2_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
