"""Independent reference geometry/virtual-work checks;not a new physical solver."""
import argparse,copy,json,math
import numpy as np
from mechanism_candidates import BASE,configs,mesh,world,guide_normal,guide_outboard,width,preflight
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=configs();results={};c=cases['baseline'];points=np.array([[x,y,z] for x in np.linspace(0,100,21) for y,z in ((-5,-.5),(0,0),(5,.1))]);old=[]
 for x,y,z in points:
  tilt=math.radians(14);xx=x*math.cos(tilt)-z*math.sin(tilt);zz=x*math.sin(tilt)+z*math.cos(tilt);old.append([50-zz,-y,-xx])
 error=float(np.max(abs(np.array(old)-np.array([world(c,p) for p in points]))));results['legacy_flat_world_bitwise']=dict(error=error,status='PASS' if error==0 else 'FAIL')
 for name,c in cases.items():
  v,t,s=mesh(c);initial=preflight(c,dict(local_positions_mm=v,tetrahedra=t,triangles=s),30,1);records=[]
  for side in (-1,1):
   route=np.array([world(c,[x,side*(width(c,x)/2+guide_outboard(c,x)),guide_normal(c,x)]) for x in [0]+c['tendon']['guide_stations']]);u=np.diff(route,axis=0);u/=np.linalg.norm(u,axis=1)[:,None];forces=-u.copy();forces[:-1]+=u[1:]
   for k,x in enumerate(c['tendon']['guide_stations']):
    base=np.array(world(c,[x,side*width(c,x)/2,0]));lever=route[k+1]-base;axis=np.array([0,1.,0]);analytic=float(np.dot(np.cross(lever,forces[k]),axis));eps=1e-6
    lengths=[]
    for h in (-eps,eps):
     q=route.copy();q[k+1]=base+lever*math.cos(h)+np.cross(axis,lever)*math.sin(h)+axis*np.dot(axis,lever)*(1-math.cos(h));lengths.append(np.linalg.norm(np.diff(q,axis=0),axis=1).sum())
    fd=-(lengths[1]-lengths[0])/(2*eps);records.append(dict(station_mm=x,side=side,moment_mm=analytic,FD_error_mm=abs(fd-analytic)))
  err=max(r['FD_error_mm'] for r in records);results[name]=dict(status='PASS' if initial['status']=='INITIAL_GEOMETRY_PASS' and err<1e-7 else 'FAIL',initial=initial,unit_tension_moment_FD_max_error_mm=err,records=records)
 a0=[r['moment_mm'] for r in results['baseline']['records']];a1=[r['moment_mm'] for r in results['A_distal']['records']];change=float(np.max(abs(np.array(a0)-a1)));results['distributed_not_constant_moment']=dict(status='PASS' if change>1e-3 else 'FAIL',maximum_moment_difference_mm=change)
 # Actual no-actuation native precurve:verify state stays at its initialized reference.
 from mechanism_assess import read
 src=BASE/'results/precurve_rest269';meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);rest=np.array([world(cfg,p) for p in local])*.001;rows=read(src/'finger0.csv');qerr=max(float(np.max(abs(np.fromstring(r['q_m'],sep=' ').reshape(-1,3)-rest))) for r in rows);verr=max(float(np.max(abs(np.fromstring(r['v_m_s'],sep=' ')))) for r in rows);results['native_stress_free_rest']=dict(status='PASS' if meta['status']=='RUN_COMPLETED_NOT_QUALIFIED' and max(qerr,verr)<=1e-12 else 'FAIL',position_error_m=qerr,velocity_error_m_s=verr,steps=len(rows),scope='four steps zero actuation at initialized curved reference;not dynamic wrapping')
 assembly=[]
 for name,c in cases.items():
  v,t,s=mesh(c);m=dict(local_positions_mm=v,tetrahedra=t,triangles=s);plain=preflight(c,m,30,3);c=copy.deepcopy(c);c['tendon']['sector_margin_mm']=.5;sector=preflight(c,m,30,3);expected_plain='INITIAL_GEOMETRY_PASS' if name=='baseline' else 'REJECT_INITIAL_GEOMETRY';expected_sector='REJECT_INITIAL_GEOMETRY' if name=='C_hybrid' else 'INITIAL_GEOMETRY_PASS';assembly.append(dict(candidate=name,plain=plain['status'],expected_plain=expected_plain,sector=sector['status'],expected_sector=expected_sector))
 results['finite_guide_assembly_guards']=dict(status='PASS' if all(r['plain']==r['expected_plain'] and r['sector']==r['expected_sector'] for r in assembly) else 'FAIL',records=assembly)
 result=dict(status='PASS' if all(r['status']=='PASS' for r in results.values()) else 'FAIL',scope='geometry/virtual work/zero-input rest only;not cable/contact/time/grasp qualification',results=results);(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:{p:v for p,v in r.items() if p not in ('initial','records')} for k,r in results.items()}))
if __name__=='__main__':main()
