"""Independent integer-pitch volume and whole-product feed-envelope checks.
Checks real thread solids,not a drawn cosmetic helix or smooth hole.
"""
import sys,json,math,shutil
from scipy.integrate import quad
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,common,bounds,overlap,volume,translate
from primary_nutseat46b import STATIONS
P=.8;K=P/(2*math.pi)

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49f_independent';out.mkdir();shutil.copyfile(__file__,out/'auditor.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};rows=[];sweeps=[];lateral=[]
 # Actual declared axial-radial profiles integrated independently over3pitches.
 # This includes sharp root/valley flats as modelled,not an ISOrootcertificate.
 re0=3.95/2;re1=4.976/2;rpe=4.456/2;ri0=4.334/2;ri1=2.6;rpi=4.605/2;L=3*P
 we=lambda r:P/4+(r-rpe)/math.sqrt(3)
 wi=lambda r:P/4+(r-rpi)/math.sqrt(3)
 ab=math.pi*re0**2+quad(lambda r:2*math.pi*r*(1-2*we(r)/P),re0,re1,epsabs=1e-12)[0]
 an=math.sqrt(3)/2*8**2-math.pi*ri1**2+quad(lambda r:2*math.pi*r*(2*wi(r)/P),ri0,ri1,epsabs=1e-12)[0]
 for pre,i,x,y,zlo,zhi,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();tip=zhi-6;bn=f'{pre}_BOLT_{i}';nn=f'{pre}_NUT_{i}';kn=f'{pre}_SOCKET_KEY_{i}';pn=f'{pre}_SPLIT_PIN_{i}'
  slab=box(x-5,y-5,tip+2.4,10,10,L)
  for n,A in [(bn,ab),(nn,an)]:
   v=common(parts[n],slab);rows.append(dict(part=n,local_z_band_mm=[2.4,4.8],pitches=3,analytic_volume_mm3=A*L,actual_BRep_volume_mm3=v,relative_volume_error=abs(v-A*L)/(A*L)))
  # Every rotating/translating bolt point stays in this axisymmetric envelope.
  # Nut screw fit is independently checked in finiteposes/classification;
  # excluding it here does NOT certify continuous thread conformity.
  env=__import__('incremental_stage1').fuse(cyl(re1,(x,y,tip),26.5),cyl(4.25,(x,y,zhi+14),11.5))
  e=bounds(env);hits=[dict(part=n,mm3=v) for n,s in parts.items() if n not in {bn,nn,kn,pn} and overlap(e,bb[n]) and (v:=common(env,s))>1e-8]
  sweeps.append(dict(bolt=bn,operation='continuous_external_obstacle_envelope_dz0to6.5_fullrotation',excluded_nut_fit=True,excluded_preinstallation_parts=[kn,pn],hits=hits))
  # Actual finite radial probes are on isolated installed bolt/nut pair.
  # Nut/cage float and head/key motion are NOT constrained by declaration.
  for axis in [0,1]:
   for sign in [-1,1]:
    vv=[]
    for e in [.07,.08]:
     v=[0.,0.,0.];v[axis]=sign*e;vv.append(common(translate(parts[bn],*v),parts[nn]))
    lateral.append(dict(bolt=bn,nut=nn,axis=axis,sign=sign,before_probe_mm=.07,before_common_mm3=vv[0],after_probe_mm=.08,after_common_mm3=vv[1],scope='Isolatedpair;NOTactualassemblyloadsequence,contactcapacity or assumed fixednuttranslation'))
 checks=dict(all128hashes_bound=len(parts)==128,integer_pitch_material_volume_agrees=all(r['relative_volume_error']<1e-5 for r in rows),continuous_external_feed_envelopes_clear=all(not s['hits'] for s in sweeps),finite_isolated_radial_contact_bracket=all(r['before_common_mm3']<1e-8 and r['after_common_mm3']>1e-5 for r in lateral))
 result=dict(status='ACTUAL_P1_THREAD_VOLUME_AND_EXTERNAL_FEED_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_THREAD_INDEPENDENT_FAIL',candidate=ref(cp),auditor=ref(out/'auditor.py'),checks=checks,integer_pitch_material=rows,maximum_material_volume_relative_error=max(r['relative_volume_error'] for r in rows),continuous_external_envelopes=sweeps,isolated_radial_contact_probes=lateral,actual_parts=len(parts),source_tolerance_pitch_diameters_mm=dict(external=[4.361,4.456],internal=[4.480,4.605]),derived_nominal_axial_gap_range_mm=[(4.480-4.456)/(2*math.sqrt(3)),(4.605-4.361)/(2*math.sqrt(3))],source_effective_engagement_mm=None,installed_capacity_N=None,actual_operating_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Volumeintegration and .07/.08mm radialprobes verify finite actualmaterial,NOTrootstress/pressure/strength/fitcertificate','Externalaxisymmetricenvelope is a continuous obstacleproof,NOTcontinuous internalthreadassembly or toolcertificate','All8oldpins and112otherpartSTEP preserved;material/host/physicalmass/operatingload/globalenergy remainblocked','Actualnut/cage/socket/key/pin finiteclearances mustbe solved together before jointloadsplit;do not fixnuttranslation or infer keyversusthreadcontactsequence fromisolatedpair'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,maxvolumeerror=result['maximum_material_volume_relative_error'],failedsweeps=[r for r in sweeps if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
