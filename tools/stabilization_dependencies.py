"""One bounded dependency retry, no ABI substitution or system installation."""
import os
import socket
import subprocess
import sys
from stabilization_common import ROOT,SOFA,OUT,write_json

def main():
    out=OUT/'dependencies';out.mkdir(parents=True,exist_ok=False);result={}
    for host in ('pypi.org','files.pythonhosted.org','repo.anaconda.com'):
        try:result[host]=socket.gethostbyname(host)
        except OSError as e:result[host]=str(e)
    result['settings_present']={key:bool(os.environ.get(key)) for key in ('HTTP_PROXY','HTTPS_PROXY','PIP_INDEX_URL','PIP_EXTRA_INDEX_URL')}
    commands={
      'pip':[sys.executable,'-m','pip','install','--isolated','--retries','0','--timeout','8','--target',str(ROOT/'.python-deps/stabilization'),'optuna>=3.6,<5'],
      'cache':[sys.executable,'-m','pip','cache','list','optuna'],
      'abi':['ldd',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')],
      'python312_offline':['/home/ubuntu/miniconda3/bin/conda','create','--prefix',str(ROOT/'.venv-sofa-stabilization'),'--offline','--solver','classic','--yes','python=3.12','numpy']}
    for name,command in commands.items():
        try:r=subprocess.run(command,capture_output=True,text=True,timeout=45);code=r.returncode;log=r.stdout+r.stderr
        except subprocess.TimeoutExpired:code=-1;log='bounded command timeout'
        (out/(name+'.log')).write_text(log);result[name]=dict(command=command,exit_code=code)
    result['optuna_available']=False
    sys.path.insert(0,str(ROOT/'.python-deps/stabilization'))
    try:import optuna;result['optuna_available']=True;result['optuna_version']=optuna.__version__
    except ImportError:pass
    write_json(out/'summary.json',result);print(result)

if __name__=='__main__':main()
