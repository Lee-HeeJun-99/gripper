"""Validate actual load-bearing Jacobian-row locations; no candidate/contact-count conflation."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=ROOT/'results'/('autonomous_film_'+a.case)/'1'
 execution=json.loads((source.parent/'summary.json').read_text());complete=execution.get('status')=='PASS' and execution.get('finite',False)
 rows=list(csv.DictReader((source/'contact_rows.csv').open()));contact=list(csv.DictReader((source/'contact.csv').open()));valid=all(None not in r and r.get('nodal_support') is not None for r in rows)
 if not valid:write_json(out/'summary.json',dict(status='FAIL',reason='Malformed row journal;original retained;not interpreted as valid points'));return
 tree=ET.parse(source/'scene.scn');center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');object_shape=tree.find('FilmNativeObserver').get('objectShape','sphere');groups={}
 for r in rows:groups.setdefault(float(r['time']),[]).append(r)
 maximum_error=0;scale=0;spans=[];max_direction=0;min_radial=1
 for r in contact:
  t=float(r['time']);sample=groups.get(t,[]);force=np.array([np.array([float(s[k]) for k in ('force_x','force_y','force_z')]) for s in sample]).reshape(-1,3).sum(axis=0);expected=np.fromstring(r['body_force'],sep=' ');maximum_error=max(maximum_error,float(np.linalg.norm(force-expected)));scale=max(scale,float(np.linalg.norm(expected)))
  if not sample:continue
  points=np.array([[float(s[k]) for k in ('begin_weighted_x','begin_weighted_y','begin_weighted_z')] for s in sample]);radial=points-center;
  if object_shape=='cylinderY':radial[:,1]=0
  unit=radial/np.linalg.norm(radial,axis=1)[:,None];span=float(np.degrees(np.arccos(np.clip((unit@unit.T).min(),-1,1))));angles=np.unwrap(np.arctan2(radial[:,2],radial[:,0]));long_span=float(np.degrees(angles.max()-angles.min()));max_direction=max(max_direction,max(float(s['column_direction_error']) for s in sample));min_radial=min(min_radial,min(float(s['radial_cosine']) for s in sample));spans.append(dict(time=t,normal_rows=len(sample),spatial_normal_span_degrees=span,longitudinal_span_degrees=long_span))
 relative=maximum_error/scale if scale else (0 if maximum_error==0 else None);ok=relative is not None and relative<1e-10 and max_direction<1e-10 and (object_shape!='sphere' or min_radial>1-1e-10)
 write_json(out/'summary.json',dict(status=('PASS' if complete else 'EXPERIMENTAL') if ok else 'FAIL',input_execution_status=execution.get('status'),trajectory_complete=complete,scope='read-only load-bearing Jacobian row reconstruction,NOT force closure/grasp qualification',absolute_force_reconstruction_error=maximum_error,relative_force_reconstruction_error=relative,maximum_column_direction_error=max_direction,minimum_radial_cosine=min_radial,object_shape=object_shape,radial_normal_qualification='limited sphere radial check' if object_shape=='sphere' else 'NOT RUN:faceted geometry has distinct normals',maximum_spatial_normal_span_degrees=max((s['spatial_normal_span_degrees'] for s in spans),default=None),maximum_longitudinal_span_degrees=max((s['longitudinal_span_degrees'] for s in spans),default=None),spans=spans,inputs={f:sha(source/f) for f in ('contact_rows.csv','contact.csv','scene.scn')},force_supported_area=None,unique_contact_points=None,pressure=None));print(json.dumps(dict(status=('PASS' if complete else 'EXPERIMENTAL') if ok else 'FAIL',relative_force_error=relative,max_longitudinal_span=max((s['longitudinal_span_degrees'] for s in spans),default=None))))
if __name__=='__main__':main()
