"""Independent bounded launcher: stop an invalid new-model run at first Newton failure.
Does not alter SOFA, states, forces, tolerances or original trial launcher.
"""
import os,resource,signal,subprocess,time
from pathlib import Path
from curve_common import sha,write_json

def guarded(command,directory,timeout=480):
    command=list(map(str,command));directory=Path(directory);directory.mkdir(exist_ok=False)
    write_json(directory/'command.json',command);started=time.monotonic();child=None
    result=dict(exit_code=None,process_status='exited',runtime_s=0.,pid=None)
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with (directory/'stdout.log').open('x') as stdout,(directory/'stderr.log').open('x') as stderr:
        try:
            child=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=limits)
            result['pid']=child.pid;write_json(directory/'process.json',dict(pid=child.pid,command=command))
            positions=[0,0];tails=['','']
            while child.poll() is None:
                for i,name in enumerate(('stdout.log','stderr.log')):
                    with (directory/name).open() as stream:
                        stream.seek(positions[i]);text=tails[i]+stream.read();positions[i]=stream.tell();tails[i]=text[-128:]
                    if 'Newton-Raphson method failed to converge' in text or '[ERROR]' in text:
                        result.update(process_status='nonlinear_failure',failure_reason='Stopped at actual SOFA Newton failure/error;partial state is invalid,not a completed trial')
                        break
                if result['process_status']!='exited':break
                if time.monotonic()-started>=timeout:result['process_status']='timeout';break
                try:child.wait(timeout=min(.1,max(.001,timeout-(time.monotonic()-started))))
                except subprocess.TimeoutExpired:pass
        except KeyboardInterrupt:result['process_status']='interrupted'
        except OSError as e:result.update(process_status='spawn_error',error=str(e))
        finally:
            if child is not None:
                if child.poll() is None:
                    try:os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                result['exit_code']=child.wait()
    result['runtime_s']=time.monotonic()-started
    result['artifacts']={p.name:sha(p) for p in directory.iterdir() if p.is_file()}
    write_json(directory/'result.json',result);return result
