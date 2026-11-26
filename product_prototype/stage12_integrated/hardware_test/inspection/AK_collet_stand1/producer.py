"""Independent actual fixture BRep/STL inventory; not proof strength."""
import argparse,json,shutil,sys
import trimesh
from baseline_registry import ROOT,REPO,S2,ref,dump,sha
sys.path.insert(0,str(S2/'scripts'))
from extract_geometry import load,properties
from OCP.BRepCheck import BRepCheck_Analyzer
def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'hardware_test/inspection'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'hardware_test/fixtures'/a.fixture/'summary.json';d=json.loads(src.read_text());rows=[]
    for r in d['parts']:
        p=REPO/r['STEP']['path'];assert sha(p)==r['STEP']['SHA256'];s=load(p);v,c,I=properties(s)
        mesh=trimesh.load(REPO/r['STL']['path'],force='mesh');error=abs(mesh.volume*1e-9/v-1)
        rows.append(dict(part=r['part'],valid=BRepCheck_Analyzer(s).IsValid(),closed=bool(mesh.is_watertight),positive=bool(mesh.is_volume),volume_relative=error))
    ok=all(r['valid'] and r['closed'] and r['positive'] and r['volume_relative']<.01 for r in rows)
    dump(out/'summary.json',dict(status='FIXTURE_GEOMETRY_AUDIT_PASS' if ok else 'FAIL',scope='Actual fixture mesh/integrals only, no proof load or hardware claim',source=ref(src),producer=ref(out/'producer.py'),rows=rows,hardware_measured=False))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',parts=len(rows))))
if __name__=='__main__':main()
