"""Complete128part local installed near-stop travel,including retained crosspins.
No omitted pin collision,physical equilibrium or contact pressure inference.
"""
import json,sys,shutil,math
from scipy.optimize import brentq
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,overlap,common,translate,box,cyl,fuse
from primary_socketcage47d import STATIONS
from validate_nutseat46c import rotate

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_profilepin48b_installedtravel';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_profilepin48b/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};rows=[];late=[]
 def hits(s,ex):
  b=bounds(s);return [dict(part_ID=n,common_mm3=v) for n,t in parts.items() if n not in ex and overlap(b,bb[n]) and (v:=common(s,t))>1e-8]
 a=brentq(lambda t:4.5*(math.cos(t)+math.sin(t))-4.6,0,.2,xtol=1e-15);b=brentq(lambda t:(3.9/math.sqrt(3))*math.cos(math.pi/6-t)-2,0,.2,xtol=1e-15)
 for prefix,i,x,y,seat,parent in STATIONS:
  for sign in [-1,1]:
   kn=f'{prefix}_SOCKET_KEY_{i}';bn=f'{prefix}_BOLT_{i}';key=rotate(parts[kn],x,y,sign*(a-1e-6));bolt=rotate(parts[bn],x,y,sign*(a+b-2e-6));ex={kn,bn};kh=hits(key,ex);bh=hits(bolt,ex);kv=common(key,bolt)
   rows.append(dict(key=kn,bolt=bn,sign=sign,key_angle_rad=sign*(a-1e-6),bolt_angle_rad=sign*(a+b-2e-6),fixed_other_parts=len(parts)-2,key_hits=kh,bolt_hits=bh,key_bolt_common_mm3=kv,retaining_pin_not_excluded=True))
 # Retest original three keepers with all eight NEW keys and pins installed.
 # Other two oldkeepers alreadyinstalled;selected pin/nut omitted only during own insertion.
 for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
  kn=f'SOCKET_KEEPER_{i}';pn=f'KEEPER_PIN_{i}';nn=f'KEEPER_NUT_{i}'
  for dz in [-30,-15,-8,-4,-2,-1,-.1,0]:late.append(dict(operation='oldkeeper_late_vertical',part=kn,dz=dz,hits=hits(translate(parts[kn],0,0,dz),{kn,pn,nn})))
  for dz in [-30,-15,-8,-4,0]:late.append(dict(operation='oldcrosspin_vertical_staging',part=pn,dz=dz,hits=hits(translate(parts[pn],-20,0,dz),{pn,nn})))
  for dx in [-20,-17,-10,-4,-1,0]:late.append(dict(operation='oldcrosspin_horizontal',part=pn,dx=dx,hits=hits(translate(parts[pn],dx,0,0),{pn,nn})))
  for dx in [20,10,5,2,0]:late.append(dict(operation='oldcrossnut_horizontal',part=nn,dx=dx,hits=hits(translate(parts[nn],dx,0,0),{nn})))
 checks=dict(all128actual_hashes_bound=len(parts)==128,installed_full_assembly_nearstops_clear=all(not r['key_hits'] and not r['bolt_hits'] and r['key_bolt_common_mm3']<1e-8 for r in rows),original_late_keeperset_paths_clear=all(not r['hits'] for r in late))
 result=dict(status='ACTUAL_P1_INSTALLED_TRAVEL_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_INSTALLED_TRAVEL_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,full_assembly_nearstop_modes=rows,old_keeper_late_poses=late,actual_parts=len(parts),key_cage_backlash_rad=a,socket_key_backlash_rad=b,serial_geometric_backlash_bound_rad=a+b,accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Finite near-stop poses;no loaded compliance/contact integration or dynamics','Finite key/socket gap does not certify preload/strength/loss or zero-backlash lock','Pin forming and supplierfullgeometry unqualified;all22systemgates remainblocked'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failed_modes=[r for r in rows if r['key_hits'] or r['bolt_hits'] or r['key_bolt_common_mm3']>1e-8],failed_oldposes=[r for r in late if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
