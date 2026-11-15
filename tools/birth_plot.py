"""Measured numerical diagnostics, never hardware performance graphics."""
import os,json
from birth_common import OUT,ROOT
os.environ['MPLCONFIGDIR']=str(OUT/'mpl_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def main():
    data=json.loads((OUT/'convergence.json').read_text());rows=[(n,r)for n,r in data['comparisons'].items()if'relative_difference'in r]
    fig,ax=plt.subplots(figsize=(10,4.5));xs=list(range(len(rows)))
    for key,offset,label in [('hold_displacement_mm',-.16,'Translation'),('hold_rotation_increment_rad',.16,'Rotation')]:
        ax.bar([x+offset for x in xs],[max(r['relative_difference'][key]*100,1e-10)for n,r in rows],width=.3,label=label)
    for x,(n,r)in zip(xs,rows):ax.plot([x-.43,x+.43],[100*r['limit']]*2,'r--',linewidth=1)
    ax.set_yscale('log');ax.set_xticks(xs,[n for n,r in rows],rotation=40,ha='right');ax.set_ylabel('Relative difference (%)');ax.set_title('Actual SOFA birth-aware diagnostics — FAILs retained; not a grasp certificate');ax.legend();fig.tight_layout();fig.savefig(ROOT/'reports/birth_evidence/convergence.png',dpi=140);plt.close(fig)
if __name__=='__main__':main()
