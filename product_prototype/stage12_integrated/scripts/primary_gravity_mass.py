"""Actual P1 CAD material slices; conditional mass quadrature, no new material rating."""
import json,sys,shutil,argparse
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def prop(s):
 g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g);p=g.CentreOfMass();return g.Mass(),np.array([p.X(),p.Y(),p.Z()])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('tag');ap.add_argument('--slices',type=int,default=32);a=ap.parse_args();assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/finger'/a.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 candidate=ROOT/'cad/exports/primaryP1_fixture15/summary.json';mass=ROOT/'validation/integrated/primaryP1_full_mass2/summary.json';cad=json.loads(candidate.read_text());m=json.loads(mass.read_text());rows=[];checks=[]
 for item in m['parts']:
  name=item['part_ID'];assert cad['part_references'][name]==item['STEP'];assert sha(REPO/item['STEP']['path'])==item['STEP']['SHA256'];c=np.array(item['centroid_mm'])*.001
  if name in ('F0_RAIL_L','F0_RAIL_R','F0_SKIN'):
   pet=name=='F0_SKIN';length=.0862 if pet else .077;shape=read(REPO/item['STEP']['path']);b=bounds(shape);edges=sorted(set([b[2],-7-length*1000,-7,b[5]]+np.linspace(-7-length*1000,-7,a.slices+1).tolist()));vols=[];mom=[]
   for z0,z1 in zip(edges[:-1],edges[1:]):
    if z1-z0<1e-8:continue
    s=BRepAlgoAPI_Common(shape,box(-100,-100,z0,300,200,z1-z0)).Shape();V,p=prop(s)
    if V<1e-9:continue
    masskg=V*1e-9*item['density_assumed_kg_m3'];mode='fixed' if p[2]>-7 else 'pet' if pet else 'rail' if p[2]>=-84 else 'terminal'
    rows.append(dict(part_ID=name,mode=mode,mass_kg=masskg,rest_centroid_m=(p*.001).tolist(),material_station_m=float(-.007-p[2]*.001),volume_mm3=V));vols.append(V);mom.append(V*p)
   checks.append(dict(part_ID=name,relative_volume_error=abs(sum(vols)/item['volume_mm3']-1),centroid_error_mm=float(np.max(abs(sum(mom)/sum(vols)-c*1000)))))
  else:
   mode='swivel' if name.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')) else 'terminal' if 'TERMINAL' in name or name.startswith(('F0_SWIVEL_AXLE','F0_SWIVEL_SLEEVE','F0_SWIVEL_SPACER')) else 'rotor' if name.startswith(('F0_STOCK_HUB','F0_SET_SCREW','F0_SPOOL','F0_DRUM')) else 'wire' if name=='F0_TENDON_WIRE' else 'fixed'
   rows.append(dict(part_ID=name,mode=mode,mass_kg=item['mass_kg'],rest_centroid_m=c.tolist()))
 total=sum(r['mass_kg'] for r in rows);assert abs(total-m['total_conditional_mass_kg'])<1e-10;assert all(r['relative_volume_error']<1e-7 and r['centroid_error_mm']<1e-6 for r in checks)
 dump(out/'mass_points.json',rows);dump(out/'inputs.json',dict(candidate=ref(candidate),mass_source=ref(mass),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/baseline_registry.py'),ref(S1/'scripts/incremental_stage1.py')],slices=a.slices))
 result=dict(status='ACTUAL_P1_CAD_MASS_SLICE_IDENTITY_PASS_CONDITIONAL_DENSITIES',candidate=ref(candidate),points=ref(out/'mass_points.json'),inputs=ref(out/'inputs.json'),slice_checks=checks,total_mass_kg=total,by_mode_kg={k:sum(r['mass_kg'] for r in rows if r['mode']==k) for k in sorted(set(r['mode'] for r in rows))},newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Exact rest slice volumes/first moments; deformed slices use section-rigid centroid quadrature,not exact deformed volume','Typical density and CAD motor/hub centroid proxies unchanged; no source-minimum mass/inertia certification','Fixed Root above-7mm; freeRail77mm and distal rigid cuff follow existing physical reduction'])
 dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
