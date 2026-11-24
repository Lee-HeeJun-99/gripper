"""Replay installed Native contact dedup on actual first-crossing detector order."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/first_crossing_phase1636';target=.0044;raw=[r for r in read(src/'detector.csv') if abs(float(r['accepted_time_s'])-target)<1e-12 and r['model0']=='/finiteEyelet/TriangleCollisionModel1' and r['model1']=='/wire/wireSurface/PointCollisionModel1'];raw.sort(key=lambda r:int(r['pair_index']));limit=float(np.float32(1e-8));kept=[];removed={}
 for r in raw:
  points=np.array([np.fromstring(r[k],sep=' ') for k in ('detected_point0','detected_point1')]);prior=next((x for x in kept if float(np.sum((x[1]-points)**2))<limit),None)
  if prior is None:kept.append((int(r['pair_index']),points))
  else:removed[int(r['pair_index'])]=dict(retained_pair=prior[0],combined_point_squared_distance_m2=float(np.sum((prior[1]-points)**2)))
 source=[r for r in read(src/'response_rows.csv') if abs(float(r['time_s'])-target)<1e-12 and r['model0']=='/finiteEyelet/TriangleCollisionModel1' and r['model1']=='/wire/wireSurface/PointCollisionModel1'];first=int(source[0]['first_row']);q0={}
 for r in read(src/'probe.children.csv'):
  if r['phase']=='build_end' and r['side']=='0' and r['constraint']==source[0]['constraint_path'] and r['state'].startswith('/finiteEyelet/TriangleCollisionModel1-PointCollisionModel1/'):
   key=(int(r['row']),int(r['column']));q0[key]=np.fromstring(r['q'],sep=' ')
 assert len(source)==len(kept);error=0.
 for j,(_,pts) in enumerate(kept):
  actual=[v for (row,col),v in q0.items() if row==first+j];assert len(actual)==1;error=max(error,float(abs(actual[0]-pts[0]).max()))
 header=Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Collision.Response.Contact/sofa/component/collision/response/contact/BaseUnilateralContactResponse.inl');assert 'constexpr double minDist2 = 0.00000001f;' in header.read_text();assert 17 in removed;d=dict(status='PASS_INSTALLED_DEDUP_REPLAY_ONLY' if error<=1e-12 else 'FAIL_NATIVE_CONTACT_ORDER_REPLAY',original_TrianglePoint_outputs=len(raw),predicted_retained_outputs=len(kept),actual_normal_constraint_rows=len(source),maximum_retained_point_vs_actual_mapping_error_m=error,installed_fixed_combined_distance_squared_limit=limit,SI_combined_distance_limit_um=float(np.sqrt(limit)*1e6),critical_detector_pair17=removed[17],retained_pair4_actual_row=first+[x[0] for x in kept].index(4),hypothesis='Actualcriticalborefacet16 detected(pair17),but fixedNative100umcombinedpointdedup discardsit in favour ofpair4/facet15 beforeconstraintassembly. Opposingmotion crossesunrepresentedfacet althoughretainednormalLCP solved. Not proof ofall errors orwholegraspfailure.',scope='Read-only exact replay ofinstalled algorithm/actualorder/actualmappedpoints;no SDKedit,thresholdrelaxation,contactremoval or newsolver. Future consistentunitcontrast needs nocontactmass/elasticity/fixturecontract FIRST;changingunits changesotherabsoluteNativeepsilonstoo,not a pure dedupfix.',source_sha256=sha(Path(__file__)),installed_header_sha256=sha(header),inputs={f:sha(src/f) for f in ('detector.csv','response_rows.csv','probe.children.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
