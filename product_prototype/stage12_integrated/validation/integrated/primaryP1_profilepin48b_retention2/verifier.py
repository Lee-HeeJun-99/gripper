"""Measure actual new pin backlash/capture before loss of support engagement.
No adoption of old0.5mmprobe as a capacity;retain it as explicit failed contrast.
"""
import json,sys,shutil,math
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,common,translate,bounds,overlap
from primary_socketcage47d import STATIONS

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_profilepin48b_retention2';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_profilepin48b/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};rows=[]
 for pre,i,x,y,seat,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();pn=f'{pre}_SPLIT_PIN_{i}';kn=f'{pre}_SOCKET_KEY_{i}';pin=parts[pn];z=seat+8.2
  for sign in [-1,1]:
   # Numerical contact threshold convergence. All2levels are retained, not caller-selected travel.
   levels=[]
   for tol in [1e-10,1e-12]:
    f=lambda dd:common(translate(pin,sign*dd,0,0),parts[parent])-tol
    dd=brentq(f,0,1.5,xtol=2e-12);levels.append(dict(common_volume_threshold_mm3=tol,withdrawal_mm=dd))
   analytic=(.2+math.sqrt((3.-.85)**2-(3.05-1.05)**2)) if sign<0 else (1.9-math.sqrt(1.8**2-(1.05**2-.9**2)))
   dd=levels[-1]['withdrawal_mm'];safe=max(0,analytic-1e-4);s=translate(pin,sign*safe,0,0);b=bounds(s)
   hits=[dict(part_ID=n,common_mm3=v) for n,t in parts.items() if n!=pn and overlap(b,bb[n]) and (v:=common(s,t))>1e-8]
   # Finite0.002mm slabs inside both actual cheek webs and key;their occupiedvolume/thickness
   # proves geometric section still crosses these stations before stop,not pressure capacity.
   slices=[]
   for off in [-5.8,0,5.8]:
    v=common(s,box(x+off-.001,y-1,z-1,.002,2,2));slices.append(dict(x_relative_mm=off,slab_width_mm=.002,pin_volume_mm3=v,mean_section_area_mm2=v/.002))
   rows.append(dict(pin=pn,parent=parent,direction=sign,stop_levels=levels,independent_analytic_stop_mm=analytic,analytic_finest_error_mm=abs(analytic-dd),analytic_stop_basis='Left: bent crown against2.1mmbore at rightcheek x7; right:3.6mmeye cylinder corner against2.1mmbore atleftcheek x-7',stop_threshold_difference_mm=abs(levels[0]['withdrawal_mm']-dd),safe_offset_mm=sign*safe,prestop_hits=hits,actual_geometric_sections=slices,old_05mm_probe_common_mm3=common(translate(pin,sign*.5,0,0),parts[parent]),old_05mm_capture_probe_pass=common(translate(pin,sign*.5,0,0),parts[parent])>1e-8,forming_removal_cycle_allowable=None,retaining_load_capacity_N=None))
 checks=dict(all128hashes_bound=len(parts)==128,each_both_directions_measured_stop=all(0<r['stop_levels'][-1]['withdrawal_mm']<1.5 for r in rows),contact_threshold_convergence=all(r['stop_threshold_difference_mm']<.001 for r in rows),independent_analytic_stop_agreement=all(r['analytic_finest_error_mm']<.001 for r in rows),before_stop_actual_wholeassembly_clear=all(not r['prestop_hits'] for r in rows),before_stop_both_cheeks_and_key_still_crossed=all(s['mean_section_area_mm2']>2 for r in rows for s in r['actual_geometric_sections']))
 result=dict(status='ACTUAL_P1_PIN_MEASURED_CAPTURE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_PIN_MEASURED_CAPTURE_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,rows=rows,actual_parts=len(parts),old_05_probe_failure_count=sum(not r['old_05mm_capture_probe_pass'] for r in rows),maximum_stop_mm=max(r['stop_levels'][-1]['withdrawal_mm'] for r in rows),maximum_threshold_change_mm=max(r['stop_threshold_difference_mm'] for r in rows),accepted_physical_product_equilibria=0,whole_system_release=False,prior_failed_threshold_result=ref(ROOT/'validation/integrated/primaryP1_profilepin48b_retention/summary.json'),limitations=['Original1e-8/1e-10mm3thresholddifference0.00134849mmFAILpreserved;new1e-10/1e-12refinementindependentlycomparedwithanalyticcontactroot','Positive undeformedgeometrycapture with finitebacklash;no ductility,springback,contactpressure,strength,fatigue orreuse certificate','Slabs show actualstationcrossing,not supportpressure orminimumsheararea under deformation','Old0.5mmprobe failures explicitlyretained;contactstops measured beforelossofsupport,no systemcriterion changed'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,maxstop=result['maximum_stop_mm'],old05fail=result['old_05_probe_failure_count'])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
