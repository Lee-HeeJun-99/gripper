"""Rerun original unit executables without modifying historical builds or results."""
from grasp_common import ROOT,OUT,write_json,sha
from run_trial import execute_process
import argparse
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='legacy_units');args=parser.parse_args()
    out=OUT/args.name;out.mkdir(exist_ok=False);results={}
    binaries=['build/revalidation_20261114_final/plugin/test_forcefield','build/next_finite_rotation/test_finite_rotation','build/integrated_20261115/plugin/test_integrated','build/stabilization_20261115/contact_fast/test_stabilization_contact','build/stabilization_20261115/compensated/test_compensated']
    for name in binaries:
        binary=ROOT/name;directory=out/binary.name;directory.mkdir()
        if not binary.exists():results[name]=dict(status='BLOCKED',reason='binary not found');continue
        command=[str(binary)];write_json(directory/'command.json',command);p=execute_process(command,directory,30);log=(directory/'stdout.log').read_text()+(directory/'stderr.log').read_text()
        # These exact messages are deliberate null/nonfinite API injections in
        # the ORIGINAL tests. They are not accepted in any simulation log.
        expected={'test_finite_rotation':['[ERROR]   [FiniteRotationShear(unnamed)] nonfinite differential input','[ERROR]   [FiniteRotationShear(unnamed)] missing matrix/state'],'test_stabilization_contact':['[ERROR]   [DistributedContact(unnamed)] contact damping matrix/state']}.get(binary.name,[])
        errors=[line.strip() for line in log.splitlines() if '[ERROR]' in line]
        results[name]=dict(status='PASS' if p['exit_code']==0 and 'PASS' in log and sorted(errors)==sorted(expected) else 'FAIL',process=p,binary_sha256=sha(binary),expected_fault_injection_errors=expected,observed_errors=errors,scope='unit-only exact expected-error assertions; SOFA scene error policy unchanged')
    write_json(out/'summary.json',results);print({k:v['status'] for k,v in results.items()})
if __name__=='__main__':main()
