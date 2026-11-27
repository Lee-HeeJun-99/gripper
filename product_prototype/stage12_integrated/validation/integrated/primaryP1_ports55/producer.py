"""Actual integrated support port topology and source trace, read-only CAD."""
import json,shutil,sys
from baseline_registry import ROOT,REPO,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from primary_motor_bearing_wrenches import faces
from primary_anchor_contact38 import common_faces,surface_moment
out=ROOT/'validation/integrated/primaryP1_ports55';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_integral55b/summary.json';d=json.loads(cp.read_text());sh={n:read(REPO/d['part_references'][n]['path']) for n in ['BENCH_SUPPORT','EXTERNAL_BENCH_PLATE','ANCHOR_NUT_0','ANCHOR_NUT_1','ANCHOR_NUT_2']};rows=[]
for n,z in [('ANCHOR_NUT_0',74),('ANCHOR_NUT_1',74),('ANCHOR_NUT_2',74),('EXTERNAL_BENCH_PLATE',-130)]:
 for s in common_faces(sh['BENCH_SUPPORT'],sh[n],2,z):
  a,c,v=surface_moment(s);rows.append(dict(other=n,z_mm=z,bounds_mm=bounds(s),area_mm2=a,centroid_mm=c.tolist()))
dump(out/'summary.json',dict(status='ACTUAL_INTEGRAL_SUPPORT_PORT_SURVEY_NOT_EQUILIBRIUM',candidate=ref(cp),producer=ref(out/'producer.py'),rows=rows,whole_system_release=False));print(json.dumps(rows))
