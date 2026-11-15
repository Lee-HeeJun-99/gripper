"""Matched-source patched headless engine; never links the installed SDK."""
from grasp_common import ROOT,OUT,BUILD,write_json,sha
from run_trial import execute_process
import argparse

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume-checkpoint',action='store_true');args=parser.parse_args()
    out=OUT/('sdk_build_resume' if args.resume_checkpoint else 'sdk_build');out.mkdir(parents=True,exist_ok=False)
    command=['cmake','--build',str(BUILD/'sofa_patched'),'--target','Sofa.SimpleApi','Sofa.Simulation.Graph','Sofa.Component.ODESolver.Backward','Sofa.Component.LinearSolver.Direct','Sofa.Component.Mass','Sofa.Component.StateContainer','Sofa.Component.AnimationLoop','-j4']
    write_json(out/'command.json',command);p=execute_process(command,out,180 if args.resume_checkpoint else 600)
    write_json(out/'result.json',dict(process=p,patch_sha256=sha(ROOT/'.runtime/MappingGraph.patch'),source_commit='7c18e95d5c5f2839079892c69e7d89a313c79603',scope='all dependencies of the tested headless components are built from matched source, no installed SOFA binaries',cache_sha256=sha(BUILD/'sofa_patched/CMakeCache.txt')));print(p)

if __name__=='__main__':main()
