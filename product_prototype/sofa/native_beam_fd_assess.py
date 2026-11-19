"""Read-only diagnostic assessment;no derivative error floor or physical PASS."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_bending_coupon import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    sources=['native_beam_loaded_fd459','native_beam_loaded_regression460','native_beam_mode_fd462','native_beam_mode_fd464','native_beam_mode_ladder465'];summaries={name:json.loads((BASE/'results'/name/'summary.json').read_text()) for name in sources}
    regression=summaries[sources[1]]['records'];assert all(r['legacy_default_FD_bytes_identical'] and r['actual_position_error_m']==0 for r in regression)
    fig,axes=plt.subplots(1,2,figsize=(10,4));records=[]
    for label,name in [('mixed','native_beam_loaded_fd459'),('bending','native_beam_mode_ladder465')]:
        for r in summaries[name]['records']:
            assert r['actual_position_error_m']==0 and r['actual_frames']==2
            for ax,key in zip(axes,['force_relative','torque_relative']):ax.loglog([v['epsilon'] for v in r['ladder']],[v[key] for v in r['ladder']],'o-',label=f'{label} nx={r["nx"]}')
            records.append(dict(direction=label,nx=r['nx'],best_force_row=r['best_force_row']))
    for ax,title in zip(axes,['Force derivative','Torque derivative']):ax.set_xlabel('Dimensionless symmetric FD step');ax.set_ylabel('Relative difference;no floor');ax.set_title(title);ax.legend(fontsize=7);ax.grid(True)
    fig.suptitle('SOFA PRIVATE force queries;NOT accepted equilibrium or grasp');fig.tight_layout();fig.savefig(out/'PRIVATE_loaded_FD.png',dpi=150);plt.close(fig)
    result=dict(scope='Read-only assessment;native directional evidence only',producer_sha256=sha(Path(__file__)),sources={name:sha(BASE/'results'/name/'summary.json') for name in sources},records=records,legacy_default_bytes_identical=True,
        decision='Mixed direction shows small relative differences;soft bending is cancellation/truncation sensitive and torque derivative near zero. No full tangent certificate or static residual remedy established. Stop tolerance/unit/FD sweeps;mesh qualification remains FAIL.',
        next='Inspect native axial strain evaluation and quantify force sensitivity to represented segment length using preserved private poses. Do not alter SDK,forces,accepted q or gates.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
