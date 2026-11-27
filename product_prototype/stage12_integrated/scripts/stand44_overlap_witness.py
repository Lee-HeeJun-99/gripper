import sys,json
from baseline_registry import ROOT,REPO,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
p=ROOT/'cad/exports/primaryP1_benchstand44c/summary.json';d=json.loads(p.read_text());s={n:read(REPO/d['part_references'][n]['path']) for n in ['TEST_BASE','BENCH_SUPPORT']};c=BRepAlgoAPI_Common(s['TEST_BASE'],s['BENCH_SUPPORT']).Shape();e=TopExp_Explorer(c,TopAbs_SOLID);rows=[]
while e.More():
 q=e.Current();rows.append(dict(bounds=bounds(q),volume=volume(q)));e.Next()
out=ROOT/'validation/integrated/primaryP1_stand44_overlap';out.mkdir();dump(out/'summary.json',dict(candidate=ref(p),common=rows));print(rows)
