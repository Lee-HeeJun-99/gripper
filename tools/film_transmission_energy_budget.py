"""Conditional accessibility of ONE no-contact static configuration,not all wraps."""
import argparse,csv,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261118_transmission_cycle_work1179','20261118_transmission_static_hybrid1165','20261118_transmission_gauss_cycle1169');data=[];hashes={}
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);d=json.loads((src/'summary.json').read_text())
  if d['status']!='PASS':raise ValueError('completed actual stage-work/static evidence required')
  for file,digest in d['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('raw evidence changed')
  data.append(d);hashes[name]=sha(src/'summary.json')
 work,static,actual=data;stages=list(csv.DictReader((ROOT/'results'/('autonomous_film_'+names[2])/'actual.csv.stages.csv').open()))
 if any(float(r['T'])!=0 for r in stages if float(r['time'])>=.03) or not actual['accumulated_clock_exact']:raise ValueError('actual post30ms load/clock differs')
 U=sum(static['endpoint'][k] for k in ('U_skin','U_rails','U_attachment'));W=work['endpoint']['tendon_work_Nmm'];D=work['endpoint']['damping_work_Nmm'];E=work['stored_plus_kinetic_Nmm'];defect=work['signed_defect_Nmm']
 if D<0 or abs(defect)>1e-8 or U<=W:raise ValueError('energy-accessibility hypothesis not supported by this dataset')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS',scope='conditional energy accessibility of one independent no-contact static shape;NOT global wrapping impossibility/full energy certification',source_summaries=hashes,static_stored_energy_Nmm=U,actual_cycle_tendon_work_Nmm=W,actual_remaining_stored_plus_kinetic_Nmm=E,actual_damping_work_Nmm=D,signed_inventory_defect_Nmm=defect,work_to_static_energy_percent=100*W/U,remaining_to_static_energy_percent=100*E/U,static_energy_minus_injected_work_Nmm=U-W,assumptions=['rest initial condition','same unchanged single-film model and fixed projected root','no object/gravity/external work','C=2M passive damping','preserved C2 pulse ends30ms;no further actuator work'],inference='Merely extending the unloaded pulse trajectory cannot reach THIS static configuration without extra work under the stated passive model. It does not exclude different lower-energy contact-guided wrapping states.',root_reaction_work=None,full_energy_gate='BLOCKED;this signed stage inventory is not whole gripper energy certification',next_test='Separate longer HOLD control at same Tmax before changing structural stiffness;requires new input/version and time refinement,not a repair of old pulse results.')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
