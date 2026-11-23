"""Bounded regression/SDK identity inventory;NOT physical certification."""
import argparse,json,re,subprocess,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 patterns=['test_contact_gap_probe.py','test_modal_load_response.py','test_first_mode_coupon.py','test_arc_candidate.py','test_layer_coupon.py','test_layer_pocket.py','test_layer_measurement.py','test_gravity_contract.py','test_ode_damping_scope.py','test_modal_deformed_ode.py','test_step_matrix.py','test_joint_footprint.py','test_load_separation.py','test_gravity_rhs.py'];records=[]
 for pattern in patterns:
  command=[sys.executable,'-m','unittest','discover','-s',str(BASE/'sofa'),'-p',pattern];r=subprocess.run(command,text=True,capture_output=True,cwd=BASE.parent);(out/(pattern+'.log')).write_text(r.stdout+r.stderr);match=re.search(r'Ran (\d+) tests?',r.stderr);records.append(dict(pattern=pattern,command=command,exit_code=r.returncode,tests=int(match.group(1)) if match else None))
 sdk=Path('/home/ubuntu/SOFA/v26.06.00');paths=[sdk/'bin/runSofa-26.06.00']+[sdk/'lib'/name for name in ('libSofa.Core.so','libSofa.Component.MechanicalLoad.so','libSofa.Component.SolidMechanics.FEM.Elastic.so','libSofa.Component.ODESolver.Backward.so','libSofa.Component.Constraint.Lagrangian.Solver.so','libSofa.Component.Constraint.Projective.so')];d=dict(status='PASS_SCOPED_REGRESSIONS_ONLY' if all(r['exit_code']==0 and r['tests'] for r in records) else 'FAIL_REGRESSION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tests=sum(r['tests'] or 0 for r in records),records=records,SDK_identity={str(f):sha(f) for f in paths if f.exists()},SDK_unavailable_paths=[str(f) for f in paths if not f.exists()],physical_validation='NOT QUALIFIED',actual_hardware='NOT MEASURED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],tests=d['tests'],SDK_files=len(d['SDK_identity']))))
if __name__=='__main__':main()
