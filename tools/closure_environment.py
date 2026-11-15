"""Read-only environment snapshots, no credentials or unfiltered environment."""
import os,platform,shutil,sys
from closure_common import ROOT,OUT,BUILD,SOFA,sha,write_json,provenance
from closure_validation_suite import logged
def main():
    out=OUT/'environment';out.mkdir(exist_ok=False);results={}
    for name,cmd in [('os',['uname','-a']),('gcc',['g++','--version']),('cmake',['cmake','--version']),('frame_linkage',['ldd',str(BUILD/'frame/libReGripFrameClosure.so')]),('python_linkage',['ldd',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')])]:results[name]=logged(cmd,out/name,15)
    import numpy,scipy,optuna
    write_json(out/'summary.json',dict(provenance=provenance(),python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,optuna=optuna.__version__,cpu_count=os.cpu_count(),memory_bytes=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'),disk_free_bytes=shutil.disk_usage(ROOT).free,workspace=str(ROOT),sdk='build/grasp_20261115/sofa_patched',runtime312=str(ROOT/'.runtime/python312'),frame_sha256=sha(BUILD/'frame/libReGripFrameClosure.so'),installed_python_missing_without_isolated_ld_path='libpython3.12.so.1.0 => not found' in (out/'python_linkage/stdout.log').read_text(),commands=results,scope='working original runtime remains isolated; bare ldd missing Python is not a recovery failure'))
if __name__=='__main__':main()
