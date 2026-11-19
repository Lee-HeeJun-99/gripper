"""All-common-time Native free-ring convergence,NO denominator floors/interpolation."""
import argparse,csv,itertools,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def compare(a,b):
 absolute=float(np.linalg.norm(a-b));den=max(float(np.linalg.norm(a)),float(np.linalg.norm(b)));return absolute,absolute/den if den else 0.
def quantities(src,meta,i):
 rows=read(src/f'0/guide{i}.csv');points=read(src/f'0/mass{i}.csv');surface=read(src/f'0/mapped{i}_eyelet.csv');root=ET.parse(src/'0/scene.scn').getroot();initial=vec(root.find(f"./Node[@name='guide{i}']/Node[@name='collision']/MechanicalObject").get('position'));q0=np.array(meta['initial'][i]['q']);R0=rotation(q0[3:]);m=meta['assumed_mass_kg'];out=[]
 for r,p,s in zip(rows,points,surface):
  q=vec(r['rigid_q']);v=vec(r['rigid_v']);x=vec(p['q']).reshape(-1,3);u=vec(p['v']).reshape(-1,3);c=x.mean(axis=0);meanv=u.mean(axis=0);H=m/len(x)*np.cross(x-c,u-meanv).sum(axis=0);Erot=m/(2*len(x))*np.sum((u-meanv)**2);Et=m/2*meanv@meanv
  out.append(dict(time_s=float(r['time_s']),values=dict(COM_displacement_m=q[:3]-q0[:3],linear_velocity_m_s=v[:3],angular_velocity_rad_s=v[3:],rotation_matrix_change=rotation(q[3:])-R0,surface_displacement_m=vec(s['q'])-initial,surface_velocity_m_s=vec(s['v']),angular_momentum_Nms=H,rotational_energy_J=np.array([Erot]),translational_energy_J=np.array([Et]),total_kinetic_energy_J=np.array([Erot+Et]))))
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=['b3_inertia_input_free593','b3_inertia_input_half595','b3_inertia_input_quarter596'];meta={c:json.loads((BASE/'results'/c/'summary.json').read_text()) for c in cases};records=[]
 if len({m['input_binary_sha256'] for m in meta.values()})!=1:raise ValueError('mixed binaries')
 if any(m['initial']!=meta[cases[0]]['initial'] for m in meta.values()):raise ValueError('mixed initial state')
 data={c:[quantities(BASE/'results'/c,meta[c],i) for i in (0,1)] for c in cases}
 for c,d in itertools.combinations(cases,2):
  ratio=round(meta[c]['dt_s']/meta[d]['dt_s'])
  if ratio*meta[d]['dt_s']!=meta[c]['dt_s']:raise ValueError('nonintegral clocks')
  for i in (0,1):
   for k,x in enumerate(data[c][i]):
    y=data[d][i][(k+1)*ratio-1]
    if abs(x['time_s']-y['time_s'])>1e-12:raise ValueError('not common actual times;no interpolation allowed')
    for name,value in x['values'].items():
     absolute,relative=compare(value,y['values'][name]);records.append(dict(cases=[c,d],body=i,time_s=x['time_s'],quantity=name,absolute_norm_error=absolute,relative_norm_error=relative,status='PASS_SELECTED_FREE_RING_TIME' if relative<=.001 else 'FAIL'))
 principal=BASE/'results/b3_inertia_input_principal598';reference=BASE/'results/b3_finite_com_principal582';purity=0.
 for variant in (0,1):
  for i in (0,1):
   for x,y in zip(read(principal/f'{variant}/guide{i}.csv'),read(reference/f'{variant}/guide{i}.csv')):
    for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(vec(x[key])-vec(y[key])))))
 worst=max(records,key=lambda r:r['relative_norm_error']);result=dict(status='PASS_SELECTED_FREE_RING_ALL_COMMON_TIME' if all(r['status']!='FAIL' for r in records) else 'FAIL_SELECTED_FREE_RING_TIME',scope='Free finite rings ONLY. All common saved Native times/all3pairs,state/shape/angular momentum/kinetic inventory. No floor/interpolation;NOT contact/B3/global energy certification. Norm relative comparisons defined per named tensor/vector. Analytically-zero input power reported separately,not hidden as energy PASS.',source_sha256=sha(Path(__file__)),records=records,worst=worst,strict_principal_control_state_difference=purity,strict_principal_control_pass=purity<=1e-12,gate=.001,source_summary_hashes={c:sha(BASE/'results'/c/'summary.json') for c in cases})
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
