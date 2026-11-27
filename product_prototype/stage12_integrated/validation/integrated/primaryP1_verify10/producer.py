"""Independent saved primary load reproduction, complex-step virtual work and manufactured mesh checks."""
import argparse,json,math,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume,common,bounds
from OCP.BRepCheck import BRepCheck_Analyzer

def point(a):
 # Stable actual terminal transform, independent of producer route/finite differences.
 ex=50-44*a*np.sinc(a/(2*np.pi))**2-5*np.sin(a)
 ez=-7-88*np.sinc(a/np.pi)-5*np.cos(a)
 return np.array([ex-7*np.cos(a)+8*np.sin(a),ez+7*np.sin(a)+8*np.cos(a)]),50-ex

def geometry(a):
 P,dx=point(a);V=P-np.array([0,20]);D=np.sqrt(V@V);u=V/D;k=11.25/D
 n=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=np.array([0,20])+11.25*n;t=(Q-P)/np.sqrt((Q-P)@(Q-P))
 ell=11.25*(np.pi/2-np.arctan(n[1]/n[0]))+np.sqrt(D*D-11.25**2)-16
 return P,Q,t,ell,dx

def mesh(path):
 vertices=[];edges={};signed=0.
 for line in path.read_text().splitlines():
  if line.strip().startswith('vertex'):vertices.append(tuple(float(x) for x in line.split()[1:]))
 for i in range(0,len(vertices),3):
  tri=vertices[i:i+3];a,b,c=map(np.array,tri);signed+=float(a@np.cross(b,c))/6
  pts=[tuple(round(x,8) for x in p) for p in tri]
  for a,b in zip(pts,pts[1:]+pts[:1]):
   key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
 return dict(triangles=len(vertices)//3,closed=bool(edges) and all(v==2 for v in edges.values()),signed_volume_mm3=signed)

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--validation',required=True);p.add_argument('--tag',required=True);a=p.parse_args();assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports'/a.candidate/'summary.json';val=ROOT/'validation/integrated'/a.validation/'summary.json';d=json.loads(src.read_text());v=json.loads(val.read_text());loads=json.loads((REPO/v['loads']['path']).read_text());inputs=json.loads((REPO/v['inputs']['path']).read_text());assert v['candidate']==ref(src)
 deps=[src,val,REPO/v['loads']['path'],REPO/v['assembly']['path'],S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
 dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),dependencies=[ref(x) for x in deps],predeclared=dict(derivative_relative_max=1e-6,work_relative_max=1e-6,load_relative_max=1e-6,STL_volume_relative_max=.01),scope='Independent nominal design and conditional prescribed-trajectory loads only, no strength or equilibrium promotion'))
 hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in inputs['dependencies']) and all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
 rows=[];drumkeys=['F0_SPOOL','F0_DRUM_NIPPLE_CAP','F0_DRUM_FACTORY_NIPPLE','F0_ROOT_BACK','OPEN_FRAME','MOTOR_CAP','GROUND_PLATE','F0_TENDON_WIRE'];meshes=[]
 for n in drumkeys:
  r=d['part_references'][n];s=read(REPO/r['path']);stl=(REPO/r['path']).with_suffix('.stl');m=mesh(stl);m.update(part_ID=n,STEP=r,STL=ref(stl),BRep_valid=bool(BRepCheck_Analyzer(s).IsValid()),CAD_volume_mm3=volume(s));m['relative_volume_error']=abs(m['signed_volume_mm3']/m['CAD_volume_mm3']-1);meshes.append(m)
 start=geometry(0)[3];dererr=[];Terr=[];strokeerr=[];tanerr=[];pointre=[];k=loads['conditional_rotational_stiffness_Nmm_rad'];h=1e-25
 for row in loads['rows']:
  ar=math.radians(row['angle_deg']);P,Q,t,ell,x=geometry(ar);Pp=np.imag(point(ar+1j*h)[0])/h;xp=np.imag(point(ar+1j*h)[1])/h
  ds=float(t@Pp);dsc=-float(np.imag(geometry(ar+1j*h)[3])/h);N=.1*9.80665/(3*row['mu_assumed']);T=(N*xp+k*ar)/ds
  dererr.append(max(abs(ds/dsc-1),abs(ds/row['stroke_derivative_mm_rad']-1)));Terr.append(abs(T/row['conditional_tension_N']-1));strokeerr.append(abs(start-ell-row['stroke_mm']));tanerr.append(abs((P-Q)@(Q-np.array([0,20]))))
  rows.append(dict(angle_deg=row['angle_deg'],mu=row['mu_assumed'],independent_stroke_derivative_mm_rad=ds,complex_step_derivative_mm_rad=dsc,conditional_T_N=float(T)))
 # Integrate independently over the actual path with Gauss rule; NOT global assembly energy.
 nodes,weights=np.polynomial.legendre.leggauss(32);work=[]
 for mu in (.2,.4,.8):
  N=.1*9.80665/(3*mu);total=0
  for z,w in zip(nodes,weights):
   ar=(z+1)*math.pi/6;P,Q,t,ell,x=geometry(ar);Pp=np.imag(point(ar+1j*h)[0])/h;xp=np.imag(point(ar+1j*h)[1])/h;ds=t@Pp;T=(N*xp+k*ar)/ds;total+=float(w*T*ds*math.pi/6)
  expected=N*float(point(math.pi/3)[1])+.5*k*(math.pi/3)**2;work.append(dict(mu=mu,tendon_work_Nmm=total,contact_plus_reference_elastic_Nmm=expected,relative_error=abs(total/expected-1)))
 # Negative control changes saved tension by1%; verifier must reject it without changing files.
 corrupt=loads['rows'][0]['conditional_tension_N']*1.01;negative=abs(rows[0]['conditional_T_N']/corrupt-1)>1e-6
 checks=dict(input_hashes=hashes,selected_BRep_valid=all(x['BRep_valid'] for x in meshes),selected_STL_closed=all(x['closed'] for x in meshes),selected_STL_volume=all(x['relative_volume_error']<.01 for x in meshes),independent_stroke_derivative=max(dererr)<1e-6,conditional_demand_reproduction=max(Terr)<1e-6,stroke_reproduction=max(strokeerr)<1e-8,tangent=max(tanerr)<1e-8,prescribed_work_identity=max(x['relative_error'] for x in work)<1e-6,perturbed_tension_rejected=negative)
 checks={k:bool(v) for k,v in checks.items()}
 result=dict(status='INDEPENDENT_PRIMARY_PARTIAL_VERIFY_PASS' if all(checks.values()) else 'INDEPENDENT_PRIMARY_VERIFY_FAIL',candidate=ref(src),validation=ref(val),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,meshes=meshes,rows=rows,work=work,derivative_relative_error_max=max(dererr),demand_relative_error_max=max(Terr),stroke_absolute_error_mm_max=max(strokeerr),tangent_error_mm2_max=max(tanerr),negative_control_original_tension_N=loads['rows'][0]['conditional_tension_N'],negative_control_changed_tension_N=corrupt,whole_system_release=False,qualified_system_gates=[],limitations=['Typical stiffness curvature reference is not a solved finite Finger','Work identity is prescribed scalar reference, not global stored energy','Capacity/physical protection and thread/bearing connector ratings remain absent','Assembly verification is finite sampling only'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,derivative_error=max(dererr))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
