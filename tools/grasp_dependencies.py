"""Scoped dependency recovery, bounded downloads; never edits system installs."""
import argparse,os,socket,subprocess,sys,time
from grasp_common import ROOT,OUT,write_json,PYTHON

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['optuna','python312','source']);args=parser.parse_args();out=OUT/'dependencies'/args.stage;out.mkdir(parents=True,exist_ok=False)
    result=dict(proxy_settings_present={k:bool(os.environ.get(k)) for k in ('HTTP_PROXY','HTTPS_PROXY','PIP_INDEX_URL','PIP_EXTRA_INDEX_URL')})
    for host in ('pypi.org','files.pythonhosted.org','conda.anaconda.org','codeload.github.com'):
        try:result[host]=socket.gethostbyname(host)
        except OSError as e:result[host]=str(e)
    if args.stage=='optuna':command=[PYTHON,'-c','import optuna,numpy,sys;print(optuna.__version__,numpy.__version__,sys.version)'];env=dict(os.environ,PYTHONPATH=str(ROOT/'.python-deps/grasp'));limit=20
    elif args.stage=='python312':command=['/home/ubuntu/miniconda3/bin/conda','create','--yes','--prefix',str(ROOT/'.runtime/python312'),'--override-channels','-c','conda-forge','python=3.12','numpy'];env=dict(os.environ,CONDA_PKGS_DIRS=str(ROOT/'.runtime/conda-pkgs'));limit=300
    else:
        (ROOT/'.runtime').mkdir(exist_ok=True);command=['curl','--fail','--location','--connect-timeout','10','--max-time','90','--output',str(ROOT/'.runtime/sofa-source.tar.gz'),'https://codeload.github.com/sofa-framework/sofa/tar.gz/7c18e95d5c5f2839079892c69e7d89a313c79603'];env=None;limit=100
    result['command']=command;start=time.monotonic()
    try:
        p=subprocess.run(command,env=env,cwd=ROOT,capture_output=True,text=True,timeout=limit);result['exit_code']=p.returncode;log=p.stdout+p.stderr
    except subprocess.TimeoutExpired as exc:result['exit_code']=None;log=str(exc)
    (out/'command.log').write_text(log);result['runtime_s']=time.monotonic()-start;write_json(out/'result.json',result);print(args.stage,result['exit_code'],log[-2000:])

if __name__=='__main__':main()
