"""Long-time static continuation and compatible symmetric linear-solver controls."""
from dataclasses import replace
from integrated_trial import Config
from stabilization_trials import run
from stabilization_common import OUT,write_json

def main():
    d=Config(layers=8,k=100,duration=.15);rows={}
    for name,c,solver in [('extended18',replace(d,duration=18),'EigenSparseLU'),('LDL',d,'SparseLDLSolver'),('CG',d,'CGLinearSolver')]:
        rows[name]=run('static_extras/'+name,c,static=True,linear=solver);write_json(OUT/'static_extras/summary.json',rows)

if __name__=='__main__':main()
