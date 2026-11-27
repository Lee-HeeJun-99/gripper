"""Full actual P1 original bolt/nut insertion under newly integral cages."""
import sys,json,shutil,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,cyl,fuse,cut
from mechanisms_stage1 import hex_axis
from primary_nutseat46b import STATIONS
from primary_installed_stack42 import overlap_area
CAD=sys.argv[1];TAG=sys.argv[2]
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/TAG;out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports'/CAD/'summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(s) for n,s in parts.items()};rows=[];seats=[]
 late={n for n in parts if '_SOCKET_KEY_' in n or '_SPLIT_PIN_' in n or n.startswith(('SOCKET_KEEPER_','KEEPER_PIN_','KEEPER_NUT_'))}
 def hits(s,exc):
  b=bounds(s);return [dict(part_ID=n,common_mm3=v) for n,t in parts.items() if n not in (exc|late) and overlap(b,bb[n]) and (v:=common(s,t))>1e-8]
 for prefix,i,x,y,z0,z1,parent in STATIONS:
  bn=f'{prefix}_BOLT_{i}';nn=f'{prefix}_NUT_{i}';seat=z1+14
  env=fuse(cyl(4.25,(x,y,seat),35),cyl(2.5,(x,y,seat-20),50))
  rows.append(dict(operation='continuous30mm_original_bolt_top_feed',part=bn,hits=hits(env,{bn,nn})))
  env=cut(hex_axis((x,y,z0-25),(0,0,1),8,29.7),cyl(2.5,(x,y,z0-25.01),29.72))
  rows.append(dict(operation='continuous25mm_original_nut_feed',part=nn,hits=hits(env,{nn})))
  env=cut(cyl(3.8,(x,y,z0-30),30),cyl(2.6,(x,y,z0-30.01),30.02))
  rows.append(dict(operation='original_annular_nutcarrier_final',part=nn,hits=hits(env,set())))
  hs=overlap_area(parts[bn],parts['BENCH_ANCHOR_RAIL'] if prefix=='BENCH_MOUNT' else parts['BENCH_SUPPORT'],seat);ns=overlap_area(parts[nn],parts[parent],z1)
  seats.append(dict(bolt=bn,nut=nn,head_seat_mm2=hs,nut_seat_mm2=ns))
 checks=dict(all_original_bolt_nut_carrier_routes_clear=all(not r['hits'] for r in rows),all_original_head_nut_seats_unchanged=all(abs(r['head_seat_mm2']-math.pi*(4.25**2-2.75**2))<1e-7 and abs(r['nut_seat_mm2']-(8**2*math.sqrt(3)/2-math.pi*2.75**2))<1e-7 for r in seats))
 result=dict(status='ACTUAL_ORIGINAL_FASTENER_ASSEMBLY_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_ORIGINAL_FASTENER_ASSEMBLY_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,actual_parts=len(parts),routes=rows,seats=seats,assembly_order=['Original eight nuts with annular carrier;anchor keepers and8newkeys/pins absent','Original eight bolts from top;real threading/preloadnotcertified','Withdrawdriver;insertnew8keysvertically','Straight8newpins stagedtopthenleft;formtipsNOTqualified','Original3anchorkeeperslast,retainingpriorverticalstagingpath'],whole_system_release=False,accepted_physical_product_equilibria=0)
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failures=[r for r in rows if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
