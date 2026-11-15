"""Static scientific figure from actual metrics; no synthetic trajectories."""
import json,os
from history_common import ROOT,OUT
os.environ['MPLCONFIGDIR']=str(OUT/'.matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def main():
    source=ROOT/'reports/history_evidence/convergence.json';r=json.loads(source.read_text());rows=[(name,c) for name,c in r['comparisons'].items() if c['status']!='NOT RUN'];fig,ax=plt.subplots(figsize=(9,4.5));x=range(len(rows));t=[100*c['relative_difference']['hold_displacement_mm'] for _,c in rows];a=[100*c['relative_difference']['hold_rotation_increment_rad'] for _,c in rows]
    ax.plot(x,t,'o-',label='translation relative difference (%)');ax.plot(x,a,'s-',label='rotation relative difference (%)');ax.axhline(1,color='red',linestyle='--',label='space/history limit 1%');ax.axhline(.1,color='orange',linestyle=':',label='time limit 0.1%');ax.set_xticks(list(x),[n for n,_ in rows],rotation=40,ha='right');ax.set_yscale('symlog',linthresh=1e-5);ax.set_ylabel('Difference (%) — fine denominator');ax.set_title('Actual SOFA history v3: separate numerical controls');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'reports/history_evidence/convergence.svg');plt.close(fig)
if __name__=='__main__':main()
