"""Exact finite polygon-annulus solid distance at saved wire vertices."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def polygon_ring_distance(points,n=32,ri=.0006,ro=.0015,half=.001):
 p=np.asarray(points);yz=p[:,1:];theta=np.arange(n)*2*np.pi/n;unit=np.column_stack([np.cos(theta),np.sin(theta)]);normals=np.column_stack([np.cos(theta+np.pi/n),np.sin(theta+np.pi/n)]);projection=(yz@normals.T).max(1);distance=[]
 for radius in (ri,ro):
  v=unit*radius;e=np.roll(v,-1,axis=0)-v;offset=yz[:,None,:]-v[None];u=np.clip(np.sum(offset*e,axis=2)/np.sum(e*e,axis=1),0,1);distance.append(np.linalg.norm(offset-u[:,:,None]*e,axis=2).min(1))
 planar=np.where(projection<ri*np.cos(np.pi/n),distance[0],np.where(projection>ro*np.cos(np.pi/n),distance[1],-np.minimum(*distance)));axial=abs(p[:,0])-half;return np.hypot(np.maximum(axial,0),np.maximum(planar,0))+np.minimum(np.maximum(axial,planar),0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--min-policy',action='store_true');p.add_argument('--guide-case');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/current_turn_wire1614';records=[]
 for name in ('no_guide_control','guide'):
  folder=BASE/'results'/a.guide_case if a.guide_case and name=='guide' else BASE/'results/wire_contact_policy1616' if a.min_policy and name=='guide' else src/name;root=ET.parse(folder/'scene.scn').getroot();rows=read(folder/'states.csv');surfaces=read(folder/'surface.csv');assert len(rows)==len(surfaces);history=[];partition=0.;impulse_rows={};actualpairs={}
  for r in read(folder/'response_rows.csv'):
   t=float(r['time_s']);impulse_rows[t]=impulse_rows.get(t,np.zeros(6))+np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
   if float(r['lambda_Ns'])!=0:actualpairs[' | '.join((r['model0'],r['model1']))]=actualpairs.get(' | '.join((r['model0'],r['model1'])),0)+1
  for r,s in zip(rows,surfaces):
   assert r['time_s']==s['time_s'];t=float(r['time_s']);points=np.fromstring(s['q'],sep=' ').reshape(-1,3);gap=polygon_ring_distance(points-[.01,0,0]);imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');partition=max(partition,float(abs(imp-impulse_rows.get(t,np.zeros(6))).max()));history.append(dict(time_s=t,minimum_vertex_solid_gap_m=float(gap.min()),negative_vertices=int(np.sum(gap<0)),contact_impulse_norm_Ns=float(np.linalg.norm(imp[:3])),solver_iterations=int(r['solver_iterations'])))
  bad=[r for r in history if r['minimum_vertex_solid_gap_m']<0];records.append(dict(guide_present=name=='guide',minimum_actual_saved_vertex_solid_gap_mm=min(r['minimum_vertex_solid_gap_m'] for r in history)*1000,first_negative_vertex_time_s=bad[0]['time_s'] if bad else None,negative_outputs=len(bad),negative_outputs_without_contact_impulse=sum(r['contact_impulse_norm_Ns']==0 for r in bad),maximum_contact_force_resultant_N=max(r['contact_impulse_norm_Ns'] for r in history)/float(root.get('dt')),maximum_solver_iterations=max(r['solver_iterations'] for r in history),source_partition_error_Ns_Nms=partition,actual_nonzero_model_pair_rows=actualpairs,status='FAIL_ACTUAL_WIRE_SOLID_INTERSECTION' if name=='guide' and bad else 'GEOMETRY_INVENTORY_ONLY',input_hashes={f:sha(folder/f) for f in ('scene.scn','states.csv','surface.csv','response_rows.csv')}));(out/f'{name}_history.json').write_text(json.dumps(history))
 d=dict(status='FINITE_WIRE_TURN_GEOMETRY_AND_RESPONSE_AUDIT_ONLY',records=records,scope='Exact signed distance to actual32sided concentric OD3/ID1.2/L2 finite annular solid;actual AdaptiveBeamMapping surfacevertices. Negativevertex proves intersection;positive doesNOTcertify continuousfacets/CCD. NoGuidecontrol usesvirtualsame reference solid only,notmissingcontactfault. NativeJlambda/dt resultant,not pressure/actuatorforce/rootreaction ormeasuredwirematerial.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
