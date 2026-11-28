import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,common
out=ROOT/'validation/integrated/primaryP1_inventory60';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_captive59c/summary.json';c=json.loads(cp.read_text());rows=[]
for n in ['F0_ROOT_BACK','BENCH_SUPPORT']:
 s=read(REPO/c['part_references'][n]['path'])
 for x in [60,64,68,70,72,76]:
  for z in [-7,-3,0,3,7,9.8,10,11,13,48.8]:
   v=common(s,box(x-1,-1,z,2,2,.2));rows.append(dict(part=n,x=x,z=z,volume_mm3=v))
dump(out/'summary.json',dict(status='ACTUAL_HOST_LOCAL_MATERIAL_INVENTORY_NOT_CAPACITY',candidate=ref(cp),rows=rows,whole_system_release=False));print(json.dumps([r for r in rows if r['volume_mm3']>.01]))
