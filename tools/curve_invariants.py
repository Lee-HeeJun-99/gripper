import shutil
from curve_common import ROOT,OUT,BUILD,PREFIX,identity,sha,write_json
from closure_validation_suite import logged
def main():
    ident=identity();out=OUT/'invariants';out.mkdir(exist_ok=False);build=ROOT/'build/autonomous_20261116_curve_a01/invariants'
    for p in(ROOT/'diagnostics/curved_contact').iterdir():
        if p.is_file():shutil.copy2(p,out/p.name)
    records={}
    for name,cmd in [('configure',['cmake','-S','diagnostics/curved_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DFROZEN_CURVE_BUILD='+str(BUILD)]),('build',['cmake','--build',build,'-j2']),('run',[build/'curved_invariants'])]:
        records[name]=logged(cmd,out/name,180)
        if records[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',records=records));return
    if identity()['curved']!=ident['curved']:raise ValueError('frozen sources changed')
    write_json(out/'summary.json',dict(status='PASS',records=records,identity=ident,binary_sha256=sha(build/'curved_invariants'),scope='actual ForceField objectivity/action reaction/Jacobian covariance,not full dynamic convergence'))
if __name__=='__main__':main()
