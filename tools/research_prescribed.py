import json,argparse
from research_common import ROOT,OUT,PREFIX,sha,write_json,identity
from closure_validation_suite import logged
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suffix',default='');args=parser.parse_args()
    if args.suffix and not args.suffix.replace('_','').isalnum():raise ValueError('suffix')
    out=OUT/('prescribed'+args.suffix);out.mkdir(exist_ok=False);build=ROOT/('build/autonomous_20261115_a01/prescribed'+args.suffix);ident=identity();write_json(out/'identity.json',ident)
    for name,command in [('configure',['cmake','-S','diagnostics/autonomous','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',build,'--target','prescribed_old','prescribed_new','-j2'])]:
        r=logged(command,out/name,180)
        if r['exit_code']:raise RuntimeError(name)
    results={}
    for model in('old','new'):
        for steps in(200,400):
            for h in(.01,.005,.0025,.00125):
                name=f'{model}_{steps}_{h}';path=out/name;r=logged([build/('prescribed_'+model),str(h),str(steps),'0'],path,120);lines=(path/'stdout.log').read_text().splitlines();values=[json.loads(t[len('PRESCRIBED '):])for t in lines if t.startswith('PRESCRIBED ')]
                results[name]=dict(status='EXPERIMENTAL'if not r['exit_code']and values else'FAIL',execution_status='PASS'if not r['exit_code']and values else'FAIL',origin='independent prescribed geometry through actual ForceField API, NOT integrated SOFA dynamics',process=r,metrics=values[-1]if values else None)
                write_json(out/'summary.json',results)
    for model in('old','new'):
        name=model+'_objective';path=out/name;r=logged([build/('prescribed_'+model),'.005','200','1.1'],path,120);values=[json.loads(t[len('PRESCRIBED '):])for t in(path/'stdout.log').read_text().splitlines()if t.startswith('PRESCRIBED ')];results[name]=dict(status='EXPERIMENTAL'if not r['exit_code']and values else'FAIL',execution_status='PASS'if not r['exit_code']and values else'FAIL',process=r,metrics=values[-1]if values else None,scope='common rigid rotation comparison to angle0,not yet assessed')
    write_json(out/'summary.json',results);print({n:r['status']for n,r in results.items()})
if __name__=='__main__':main()
