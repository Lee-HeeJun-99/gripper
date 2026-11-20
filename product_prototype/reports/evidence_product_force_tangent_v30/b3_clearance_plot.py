"""Actual Native saved-state gap comparison;no conceptual deformation."""
import argparse,csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);fig,axes=plt.subplots(1,2,figsize=(12,4));inputs={}
 for case,label in [('b3_guide_clearance472','baseline375'),('b3_guide_clearance476','sector margin1mm474'),('b3_window_clearance488','alarm window485')]:
  path=BASE/'results'/case/'sampled_gap.csv';rows=list(csv.DictReader(path.open()));axes[0].plot([float(r['actual_time_s']) for r in rows],[float(r['minimum_native_guide_sphere_gap_mm']) for r in rows],label=label);inputs[str(path.relative_to(BASE))]=sha(path)
 axes[0].set(xlim=(2.37,2.41),ylim=(-1.3,5),xlabel='Actual SOFA time [s]',ylabel='Minimum guide-sphere gap [mm]',title='Actual 3-finger release;dt2.5ms')
 axes[0].axhline(0,color='k',linestyle='--');axes[0].axvspan(2.386,2.396,alpha=.1,color='green');axes[0].legend(fontsize=7)
 for case,label in [('b3_guide_pair483','dt2.5ms'),('b3_guide_pair_half496','dt1.25ms'),('b3_guide_pair_quarter497','dt0.625ms')]:
  path=BASE/'results'/case/'summary.json';d=json.loads(path.read_text());r=d['records'][1];n=r['frames'];axes[1].plot([.01*(i+1)/n for i in range(n)],r['gap_mm'],'o-',label=label);inputs[str(path.relative_to(BASE))]=sha(path)
 axes[1].set(xlabel='Native FREE-pair coupon time [s]',ylabel='Actual saved gap [mm]',title='Alarm5mm:clearance is NOT time convergence');axes[1].legend(fontsize=7)
 fig.suptitle('SOFA v26.06;research assumptions;NOT whole clearance,mesh/time or grasp certification',fontsize=10);fig.tight_layout();fig.savefig(out/'actual_native_clearance.png',dpi=160);plt.close(fig)
 result=dict(scope='Actual Native saved-state scientific plot;no deformation scaling or hidden object relocation',source_sha256=sha(Path(__file__)),inputs=inputs,physical_case485='R30mm,50g,gravity9.81,mu0.3 assumed,1.5N per cable;source18bd3eb;physical binary3eb202b1e2a;alarm module6da7c82044b7',time_convergence='FAIL preserved498')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
