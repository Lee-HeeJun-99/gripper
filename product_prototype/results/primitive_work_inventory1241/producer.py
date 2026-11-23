"""Actual accepted-state BE translational inventory;not whole energy certification."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def inventory(case):
 src=BASE/'results'/case;pre=json.loads((src/'preflight.json').read_text());dt=pre['dt_s'];mass=pre['mass_kg'];force=pre.get('tangential_force_N',.01);qprev=np.array([pre.get('initial_x_m',0),0,pre['radius_m']+pre['initial_gap_m']]);vprev=np.zeros(3);sums=np.zeros(6);maxbalance=0.;maxkinematics=0.;trace=[];maxomega=0.
 with (src/'rigid.csv').open() as f:rows=list(csv.DictReader(f))
 for r in rows:
  t=float(r['time_s']);tau=t-dt;q=np.fromstring(r['rigid_q'],sep=' ')[:3];vfull=np.fromstring(r['rigid_v'],sep=' ');v=vfull[:3];I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3];F=np.array([force*np.clip((tau-.01)/.002,0,1),0,-.4*np.clip(tau/.01,0,1)]);dK=.5*mass*(v@v-vprev@vprev);Wext=dt*(F@v);Wtan=I[:2]@v[:2];Wnormal=I[2]*v[2];Wdamp=-dt*mass*(v@v);Lnum=.5*mass*((v-vprev)@(v-vprev));balance=dK-Wext-Wtan-Wnormal-Wdamp+Lnum;maxbalance=max(maxbalance,abs(float(balance)));maxkinematics=max(maxkinematics,float(abs(q-qprev-dt*v).max()));maxomega=max(maxomega,float(np.linalg.norm(vfull[3:])));sums+=[dK,Wext,Wtan,Wnormal,Wdamp,Lnum];trace.append(dict(time_s=t,kinetic_energy_J=float(.5*mass*(v@v)),external_work_J=float(sums[1]),tangential_contact_work_J=float(sums[2]),normal_contact_work_J=float(sums[3]),damping_work_J=float(sums[4]),BE_numerical_loss_J=float(sums[5]),step_balance_J=float(balance)));qprev=q;vprev=v
 return dict(case=case,status='PASS_TRANSLATIONAL_DISCRETE_IDENTITY_ONLY' if maxbalance<1e-12 and maxkinematics<1e-12 else 'FAIL_DISCRETE_IDENTITY',delta_kinetic_J=float(sums[0]),external_work_J=float(sums[1]),tangential_contact_work_J=float(sums[2]),normal_contact_work_J=float(sums[3]),damping_work_J=float(sums[4]),BE_numerical_loss_J=float(sums[5]),cumulative_balance_J=float(sums[0]-sums[1]-sums[2]-sums[3]-sums[4]+sums[5]),maximum_step_balance_abs_J=maxbalance,maximum_q_step_error_m=maxkinematics,maximum_angular_speed_rad_s=maxomega,fixture_reaction_work=None,whole_system_energy=None,scope='End-step BE quadrature and measured impulses. Numerical loss is NOT physical heat. Tangential work is discrete contact work,not calibrated continuous friction loss. No force/pressure inferred from row counts.',input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('rigid.csv','preflight.json')}),trace
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('primitive_offset_slip1230','primitive_offset_stick1231','primitive_offset_sliding1232'):
  record,trace=inventory(case);records.append(record);(out/(case+'.json')).write_text(json.dumps(trace,indent=2))
 d=dict(status='SCOPED_DISCRETE_WORK_INVENTORY_ONLY',records=records,physical_product_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
