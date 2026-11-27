"""Partitioned actual P1 installed helical pair queries; durable per-operation journal."""
import sys,json,math,shutil,time,os
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from validate_nutseat46c import rotate
from primary_nutseat46b import STATIONS

def main():
 mode=sys.argv[1];idx=int(sys.argv[2]);out=ROOT/'validation/integrated'/f'primaryP1_pair50_{mode}_{idx}';out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 pre,i,x,y,zlo,zhi,parent=STATIONS[idx];bn=f'{pre}_BOLT_{i}';nn=f'{pre}_NUT_{i}';br=cad['part_references'][bn];nr=cad['part_references'][nn];b=read(REPO/br['path']);n=read(REPO/nr['path']);rows=[];checks={};K=.8/(2*math.pi)
 dump(out/'inputs.json',dict(candidate=ref(cp),bolt=br,nut=nr,station=STATIONS[idx],producer=ref(out/'producer.py'),scope='Actual installed pair only;nut held for relative-coordinate geometry,NOT ground fixation or installed joint equilibrium'))
 def query(dz,theta,label):
  assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(event='START',dz_mm=dz,theta_rad=theta,label=label))+'\n');f.flush();os.fsync(f.fileno())
  v=common(translate(rotate(b,x,y,theta),0,0,dz),n);r=dict(event='COMPLETE',dz_mm=dz,theta_rad=theta,label=label,common_mm3=v,elapsed_s=time.monotonic()-t);rows.append(r)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
  print(json.dumps(r),flush=True);return v
 if mode in ['feed','combined']:
  for dz in [0.,.2,.4,.8,1.6,3.2,6.5]:query(dz,dz/K,'RH_screw_relative_feed')
  checks=dict(sampled_RH_feed_clear=all(r['common_mm3']<1e-8 for r in rows))
 if mode in ['axial','combined']:
  for dz in [-.05,-.04,.04,.05]:query(dz,0.,'fixed_relative_rotation_axial_probe')
  checks.update(both_sign_axial_contact_bracket=all(r['common_mm3']<1e-8 if abs(r['dz_mm'])==.04 else r['common_mm3']>1e-5 for r in rows if r['label']=='fixed_relative_rotation_axial_probe'))
 if mode not in ['feed','axial','combined']:raise ValueError(mode)
 dump(out/'summary.json',dict(status='ACTUAL_P1_PAIR_LOCAL_GEOMETRY_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_PAIR_GEOMETRY_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),journal=ref(out/'journal.jsonl'),checks=checks,rows=rows,analytic_clearance_mm=(4.605-4.456)/(2*math.sqrt(3)),accepted_product_equilibria=0,installed_capacity_N=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Finite sampled poses are NOT continuous internal fit proof','Nut/cage/head/key/pin coupled DOFs and pressure/strength remain unqualified','No operating100g,friction,Finger,ultimate host or global energy qualification']))
 raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
