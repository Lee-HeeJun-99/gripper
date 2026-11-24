"""Trace actually penetrating wire vertices into Native detector/Jacobian rows."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from current_turn_wire_assess import polygon_ring_distance
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/identified_contact_phase1626';meta=json.loads((src/'summary.json').read_text());target=meta['target_accepted_time_s'];surface=read(src/'surface.csv');now=np.fromstring(surface[-1]['q'],sep=' ').reshape(-1,3);prev=np.fromstring(surface[-2]['q'],sep=' ').reshape(-1,3);gn=polygon_ring_distance(now-[.01,0,0]);gp=polygon_ring_distance(prev-[.01,0,0]);ids=np.flatnonzero(gn<0);rows={int(r['row']):float(r['f']) for r in read(src/'probe.rows.csv') if r['phase']=='solve_end'};source={int(r['row_id']):r for r in read(src/'response_rows.csv') if abs(float(r['time_s'])-target)<1e-12};J={}
 for r in read(src/'probe.children.csv'):
  if r['phase']!='build_end' or r['state']!='/wire/wireSurface/surface':continue
  key=(int(r['row']),int(r['column']));v=np.fromstring(r['J'],sep=' ')
  if key in J:assert np.array_equal(J[key],v)
  J[key]=v
 detector=[r for r in read(src/'detector.csv') if abs(float(r['accepted_time_s'])-target)<1e-12];records=[]
 for index in ids:
  matches=[]
  for r in detector:
   for side in (0,1):
    if r[f'model{side}']=='/wire/wireSurface/PointCollisionModel1':
     error=float(np.linalg.norm(np.fromstring(r[f'detected_point{side}'],sep=' ')-prev[index]));
     if error<=1e-12:matches.append(dict(model0=r['model0'],model1=r['model1'],point_error_m=error))
  influence=[]
  for (row,col),v in J.items():
   if col!=index or np.linalg.norm(v)==0:continue
   r=source[row];influence.append(dict(row=row,model0=r['model0'],model1=r['model1'],J=v.tolist(),lambda_Ns=rows[row],vertex_impulse_Ns=(v*rows[row]).tolist()))
  records.append(dict(vertex=int(index),previous_actual_solid_gap_m=float(gp[index]),accepted_actual_solid_gap_m=float(gn[index]),step_displacement_m=(now[index]-prev[index]).tolist(),actual_point_detector_matches=matches,actual_source_resolved_row_influences=influence))
 d=dict(status='ACTUAL_PENETRATING_VERTEX_CONTACT_PROVENANCE_ONLY',target_time_s=target,records=records,scope='OriginalwireSurfaceJacobian deduplicatedbyglobalrow/vertex acrosssharedstatequeries;allactualrowforcecontributions retained. Detectorpoints matchedtoPREVIOUSacceptedpoint only,notcurrentpose or inferredfeatureID. Positive/negative signedsolidgap distinctfromfrozencontacthalfspace. Notforcecorrection,CCD/reintegration orwholegraspqualification.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('surface.csv','probe.children.csv','probe.rows.csv','response_rows.csv','detector.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
