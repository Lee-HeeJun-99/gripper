"""Isolated SOFA trials with exclusive output ownership and complete failure records."""
import argparse
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
from native_scene import generate
from verification_common import ROOT, SOFA, BUILD, provenance, sha, write_json,assert_build_current
from trial_validation import TrialError, analyze, validate_config, verify_artifacts


def execute_process(command,out,timeout):
    """Always reap the child, including cancellation and timeout."""
    out=Path(out);started=time.monotonic();process=None
    result=dict(exit_code=None,process_status='exited',runtime_s=0.,pid=None)
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with (out/'stdout.log').open('x') as stdout,(out/'stderr.log').open('x') as stderr:
        try:
            process=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=limits)
            result['pid']=process.pid
            write_json(out/'process.json',dict(pid=process.pid,command=command))
            result['exit_code']=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['process_status']='timeout'
        except KeyboardInterrupt:
            result['process_status']='interrupted'
        except OSError as exc:
            result.update(process_status='spawn_error',error=str(exc))
        finally:
            if process is not None:
                if process.poll() is None:
                    try:os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                result['exit_code']=process.wait()
    result['runtime_s']=time.monotonic()-started
    return result


def run_trial(out,k=None,connectors=None,dt=.0005,duration=3.,load=.0001,n=11,timeout=60):
    steps=validate_config(k,connectors,dt,duration,load,n,timeout)
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)  # Atomic ownership; never reuse partial output.
    config=dict(k=k,connectors=sorted(connectors) if connectors is not None else None,dt=dt,duration=duration,
                load=load,n=n,timeout=timeout,length_mm=30,layer_thickness_mm=.4,young_modulus=250,
                poisson_ratio=.32,total_mass=2e-5,force_units='model force units; not calibrated to physical PET',seed=11)
    diag=BUILD/'diagnostics/libReGripDiagnostics.so';plugin=BUILD/'plugin/bin/libSofaTangentialV110.so'
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(steps),
             '--hideProgressBar','-l',str(diag)]
    if k is not None:command+=['-l',str(plugin)]
    command+=[str(out/'scene.scn')]
    report=dict(config=config,status='crash',failure_reason='',exit_code=None,execution_completed=False,
                equilibrium_validated=False,effective_stiffness=None,sofa_version='26.06.00',**provenance())
    write_json(out/'config.json',config);write_json(out/'command.json',command)
    write_json(out/'metrics.json',dict(report,status='incomplete'))
    try:
        assert_build_current()
        report['build_manifest_sha256']=sha(BUILD/'build_manifest.json')
        report.update(plugin_sha256=sha(plugin) if k is not None else None,diagnostics_sha256=sha(diag))
        generate(out/'scene.scn',dt,load,k,config['connectors'],n)
        report['scene_sha256']=sha(out/'scene.scn')
        result=execute_process(command,out,timeout);report.update(result)
        log=(out/'stdout.log').read_text()+'\n'+(out/'stderr.log').read_text()
        (out/'sofa.log').write_text(log)
        if result['process_status']!='exited':
            report.update(status='timeout' if result['process_status']=='timeout' else 'crash',
                          failure_reason=result['process_status']+': '+result.get('error',''))
        else:report.update(analyze(out,config,result['exit_code'],log))
    except TrialError as exc:report.update(status=exc.status,failure_reason=str(exc))
    except (OSError,ValueError,KeyError,OverflowError,RuntimeError) as exc:report.update(status='crash',failure_reason=str(exc))
    report['artifact_sha256']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json' and not p.name.endswith('.partial')}
    write_json(out/'metrics.json',report)
    print(out.name,report['status'],'tip=',report.get('tip_deflection_mm'),'residual=',report.get('relative_residual'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out');parser.add_argument('--k',type=float)
    parser.add_argument('--dt',type=float,default=.0005);parser.add_argument('--duration',type=float,default=3.)
    parser.add_argument('--connectors',type=int,nargs='+');parser.add_argument('--nodes',type=int,default=11)
    parser.add_argument('--load',type=float,default=.0001);parser.add_argument('--timeout',type=float,default=60.)
    a=parser.parse_args()
    try:result=run_trial(a.out,a.k,a.connectors,a.dt,a.duration,a.load,a.nodes,a.timeout)
    except (ValueError,FileExistsError) as exc:parser.error(str(exc))
    raise SystemExit(0 if result['status']=='complete' else 1)
