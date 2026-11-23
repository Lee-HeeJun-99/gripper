"""Extended precision segment distance reference,not certified moving-wire CCD."""
import argparse,itertools,json,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha,sector

def closest_polylines(first,second):
 P,Q=np.asarray(first,dtype=np.longdouble),np.asarray(second,dtype=np.longdouble)
 if any(x.ndim!=2 or x.shape[1]!=3 or len(x)<2 or not np.all(np.isfinite(x)) for x in (P,Q)):raise ValueError('finite Nx3 polylines required')
 u=np.diff(P,axis=0)[:,None,:];v=np.diff(Q,axis=0)[None,:,:];w=P[:-1,None,:]-Q[None,:-1,:]
 a=np.sum(u*u,axis=2);b=np.sum(u*v,axis=2);c=np.sum(v*v,axis=2);d=np.sum(u*w,axis=2);e=np.sum(v*w,axis=2)
 if np.any(a==0) or np.any(c==0):raise ValueError('zero-length segment')
 best=np.full(w.shape[:2],np.inf,dtype=np.longdouble);best_s=best.copy();best_t=best.copy()
 def candidate(s,t,valid=True):
  nonlocal best,best_s,best_t
  distance2=np.sum((w+s[...,None]*u-t[...,None]*v)**2,axis=2);mask=(distance2<best)&valid
  best=np.where(mask,distance2,best);best_s=np.where(mask,s,best_s);best_t=np.where(mask,t,best_t)
 z=np.zeros_like(best);o=np.ones_like(best)
 candidate(z,np.clip(e/c,0,1));candidate(o,np.clip((e+b)/c,0,1));candidate(np.clip(-d/a,0,1),z);candidate(np.clip((b-d)/a,0,1),o)
 det=np.sum(np.cross(u,v)**2,axis=2);nz=det>0;safe=np.where(nz,det,1);s=(b*e-c*d)/safe;t=(a*e-b*d)/safe
 candidate(s,t,nz&(s>=0)&(s<=1)&(t>=0)&(t<=1))
 i,j=np.unravel_index(np.argmin(best),best.shape);s,t=best_s[i,j],best_t[i,j]
 return dict(distance_mm=float(np.sqrt(best[i,j])),segment_indices=[int(i),int(j)],parameters=[float(s),float(t)],closest_points_mm=[(P[i]+s*(P[i+1]-P[i])).astype(float).tolist(),(Q[j]+t*(Q[j+1]-Q[j])).astype(float).tolist()])

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--finger-chain-case');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.finger_chain_case) if n):p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();sources=[BASE/'results'/n/'summary.json' for n in ('product_supplier_first_recheck890','product_supplier_second_full_wire887')];routes={}
 for finger,cable in itertools.product(range(3),range(2)):
  S=sector(120*finger);r=np.asarray(json.loads(sources[cable].read_text())['route_mm']);routes[f'f{finger}_c{cable}']=r@S[:3,:3].T+S[:3,3]
 extra=[]
 if a.finger_chain_case:
  for name,lead in list(routes.items()):
   f=BASE/'results'/a.finger_chain_case/('lead_'+name+'.json');raw=json.loads(f.read_text());chain=np.asarray(raw['route_mm'])
   if np.linalg.norm(chain[0]-lead[0])>1e-10:raise ValueError('chain/lead origin mismatch')
   routes[name]=np.vstack([chain[::-1],lead[1:]]);extra.append(f)
 records=[]
 for x,y in itertools.combinations(routes,2):
  r=closest_polylines(routes[x],routes[y]);records.append(dict(pair=[x,y],**r,nominal_wire_surface_gap_mm=r['distance_mm']-.45,sagitta_expanded_gap_mm=r['distance_mm']-2*.22522275007459786))
 result=dict(status='REST_LEAD_PAIR_DISTANCE_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),BASE/'cad/manufacturing_assembly.py',*sources)},records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='15pairs of6REST lead numericalpolylines ONLY,not entirefingerwire/movingclearance. longdouble segment minimization including endpoints/interior witnesses;NOT intervalarithmetic/exactcertificate. .45mm nominal diameters plus inherited arc sagitta budget reported separately,notmanufacturingtolerance. No wirefriction/elasticity/contactlaw/Native/holding/STEPqualification.')
 for f in extra:result['input_hashes'][str(f.relative_to(BASE))]=sha(f)
 result['finger_chain_case']=a.finger_chain_case
 if a.finger_chain_case:result['scope']='15pairs of6REST distalguide→otherguidecentres→Root→3turns→drum numericalpolylines,NOT anchor/pulltermination or movingwire. Extendedprecision segment reference+nominalwire/sagitta gaps,NOT exact/intervalcertified clearance or actualwirecontact/friction/fatigue/Native/STEPqualification.'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],minimum_expanded_gap_mm=min(r['sagitta_expanded_gap_mm'] for r in records),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
