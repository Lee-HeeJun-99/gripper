"""Independent analytic 2D cage section vs actual BRep intersections.
No contact pressure, material limit, or installed thread inferred.
"""
import sys,json,math,shutil
import numpy as np
from scipy.integrate import quad
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,common,bounds,overlap
from primary_installed_stack42 import cylinders

def poly(af,t=0):
 return [(af/math.sqrt(3)*math.cos(t+k*math.pi/3),af/math.sqrt(3)*math.sin(t+k*math.pi/3)) for k in range(6)]
def interval(vertices,x):
 ys=[]
 for (a,b),(c,d) in zip(vertices,vertices[1:]+vertices[:1]):
  if min(a,c)<=x<=max(a,c) and abs(c-a)>1e-14:ys.append(b+(d-b)*(x-a)/(c-a))
 return (min(ys),max(ys)) if ys else None
def collision_area(af,t):
 nut=poly(af,t);hole=poly(8.2);corners=poly(8.2);xmin=min(p[0] for p in nut);xmax=max(p[0] for p in nut)
 def length(x):
  n=interval(nut,x)
  if n is None:return 0.
  pieces=[];h=interval(hole,x)
  if h:pieces.append(h)
  for cx,cy in corners:
   r2=.36-(x-cx)**2
   if r2>0:
    r=math.sqrt(r2);pieces.append((cy-r,cy+r))
  spans=sorted((max(a,n[0]),min(b,n[1])) for a,b in pieces if min(b,n[1])>max(a,n[0]));covered=0.;end=n[0]
  for a,b in spans:covered+=max(0.,b-max(end,a));end=max(end,b)
  return max(0.,n[1]-n[0]-covered)
 # Integrate on exact boundary events. Unsplit adaptive quadrature can
 # miss narrow contact slivers and report a misleading small estimator.
 events=[xmin,xmax,*[x for x,y in nut+hole],*[x+d for x,y in corners for d in (-.6,0,.6)]]
 edges=lambda p:list(zip(p,p[1:]+p[:1]))
 for aa,bb in edges(nut)+edges(hole):
  a=np.array(aa);d=np.array(bb)-a
  for cc in corners:
   u=a-np.array(cc);coef=[float(d@d),float(2*u@d),float(u@u-.36)]
   for z in np.roots(coef):
    if abs(z.imag)<1e-12 and 0<=z.real<=1:events.append(float(a[0]+z.real*d[0]))
 for aa,bb in edges(nut):
  a=np.array(aa);d=np.array(bb)-a
  for cc,dd in edges(hole):
   c=np.array(cc);e=np.array(dd)-c;M=np.column_stack([d,-e])
   if abs(np.linalg.det(M))>1e-12:
    u,w=np.linalg.solve(M,c-a)
    if 0<=u<=1 and 0<=w<=1:events.append(float(a[0]+u*d[0]))
 knots=[]
 for x in sorted(events):
  if xmin<=x<=xmax and (not knots or x-knots[-1]>1e-12):knots.append(x)
 values=[quad(length,a,b,epsabs=1e-11,epsrel=1e-10,limit=200) for a,b in zip(knots,knots[1:])]
 return sum(v for v,e in values),sum(e for v,e in values)
def stop(af):
 lo=0.;hi=.3
 for _ in range(28):
  mid=(lo+hi)/2
  if collision_area(af,mid)[0]*4.7>1e-8:hi=mid
  else:lo=mid
 return [lo,hi]
def main():
 out=ROOT/'validation/integrated/primaryP1_nutcapture43b_independent_split';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists()
 vp=ROOT/'validation/integrated/primaryP1_nutcapture43b_validation/summary.json';v=json.loads(vp.read_text());cp=REPO/v['candidate']['path'];assert sha(cp)==v['candidate']['SHA256'];cad=json.loads(cp.read_text());refs=cad['part_references'];rail=read(REPO/refs['BENCH_ANCHOR_RAIL']['path']);rows=[]
 for r in v['rows']:
  for t in r['stops']:
   theta=t['sign']*(t['interference_angle_rad']+.01);a,e=collision_area(8,theta);expect=a*4.7;actual=t['probe_plus_001rad_volume_mm3'];rows.append(dict(station=r['station'],angle_rad=theta,analytic_area_mm2=a,quadrature_error_mm2=e,analytic_volume_mm3=expect,BRep_volume_mm3=actual,absolute_error_mm3=abs(expect-actual)))
 smax=stop(8);smin=stop(7.78);cy=cylinders(rail);mounts=[];ports=[(-59,-58),(101,-58),(-59,39),(101,39)];s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(sh) for n,sh in s.items()}
 for x,y in ports:
  found=[c for c in cy if abs(c['radius_mm']-2.75)<1e-8 and abs((c['bounds_mm'][0]+c['bounds_mm'][3])/2-x)<1e-7 and abs((c['bounds_mm'][1]+c['bounds_mm'][4])/2-y)<1e-7]
  # Head-sized upper insertion corridor for potential M5 fastener, no
  # fastener selection/retention/external body is inferred from this volume.
  tool=cyl(4.25,(x,y,74),25);b=bounds(tool);hits=[dict(part_ID=n,volume_mm3=z) for n in s if overlap(b,bb[n]) and (z:=common(tool,s[n]))>1e-8]
  mounts.append(dict(xy_mm=[x,y],actual_cylinder_faces=found,upper_head_sweep_hits=hits))
 independent_stop=max(abs(sum(smax)/2-t['interference_angle_rad']) for r in v['rows'] for t in r['stops'])
 checks=dict(independent_cage_section_BRep_volume=all(r['absolute_error_mm3']<1e-7 for r in rows),independent_stop_angle=independent_stop<3e-7,source_min_nut_backlash_larger=smin[0]>smax[1],four_actual_through_mount_ports=all(len(m['actual_cylinder_faces'])==1 and abs(m['actual_cylinder_faces'][0]['bounds_mm'][2]-66)<1e-7 and abs(m['actual_cylinder_faces'][0]['bounds_mm'][5]-74)<1e-7 for m in mounts))
 dump(out/'summary.json',dict(status='INDEPENDENT_ACTUAL_P1_CAGE_SECTION_AND_MOUNT_AUDIT_NOT_RELEASE',candidate=ref(cp),parent_validation=ref(vp),verifier=ref(out/'verifier.py'),actual_parts=85,checks=checks,cage_section_comparisons=rows,source_max8AF_stop_interval_rad=smax,source_min7_78AF_stop_interval_rad=smin,independent_stop_error_rad=independent_stop,mounting_ports=mounts,all_mount_head_sweeps_clear=all(not m['upper_head_sweep_hits'] for m in mounts),external_support_body=None,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Dimensional max/min nut contrast only;not process tolerances/certified delivered parts.','Head-sized corridor is a geometry feasibility check,not a fastener installation or external support.','No physical bolt lock,threadcore/flank/material/strength,externalbench or operating sourcefield is qualified.']))
 print(json.dumps(dict(checks=checks,stops=[smax,smin],mounts=mounts)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
