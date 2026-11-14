"""Export standalone comparison figures from measured CSV, using Matplotlib."""
import csv
import json
from pathlib import Path
import sys
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from baseline_regression import ROOT


def read(path):
    with Path(path).open(encoding='utf-8-sig') as stream:return list(csv.DictReader(stream))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,default=ROOT/'results/physics_validation')
    parser.add_argument('--out',type=Path,default=ROOT/'reports')
    args=parser.parse_args()
    out=args.out
    if any((out/name).exists() for name in ('baseline_comparison.png','equilibrium_sweep.png')):raise FileExistsError('refusing existing figures')
    out.mkdir(parents=True,exist_ok=True)
    actual=read(args.results/'baseline/baseline_free.csv')
    golden=read(ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv')
    fig,axes=plt.subplots(1,2,figsize=(10,3.5))
    for ax,key,label in zip(axes,['tip_deflection_mm','max_x_slip_mm'],['Tip deflection (mm)','Interface X slip (mm)']):
        ax.plot([float(r['time_s']) for r in golden],[float(r[key]) for r in golden],label='Windows V109',linewidth=2)
        ax.plot([float(r['time_s']) for r in actual],[float(r[key]) for r in actual],'--',label='Ubuntu native adapter')
        ax.set(xlabel='Time (s)',ylabel=label);ax.grid(alpha=.3);ax.legend()
    fig.tight_layout();fig.savefig(out/'baseline_comparison.png',dpi=180);plt.close(fig)
    summary=read(args.results/'summary.csv')
    ks=['k001','k01','k1','k10','k100'];data=[next(r for r in summary if r['case']==case) for case in ks]
    fig,axes=plt.subplots(1,2,figsize=(10,3.5))
    refs=read(args.results/'reference_comparison.csv')
    free=float(next(r for r in refs if float(r['k'])==0)['rectangular_tip'])
    for key,label in [('rectangular_tip','V106 rectangular reference'),('circular_tip','Equivalent circular reference')]:
        pos=[r for r in refs if float(r['k'])>0]
        axes[0].semilogx([float(r['k']) for r in pos],[free/float(r[key]) for r in pos],label=label)
    axes[0].semilogx([float(r['k']) for r in data],[float(r['stiffness_ratio']) for r in data],'o',label='SOFA equilibrium')
    axes[0].set(xlabel='Per-connector k (model units)',ylabel='Stiffness ratio to same FREE model')
    axes[0].legend(fontsize=8);axes[0].grid(alpha=.3)
    axes[1].loglog([float(r['k']) for r in data],[float(r['slip']) for r in data],'o-')
    axes[1].set(xlabel='Per-connector k (model units)',ylabel='All-node max X slip (mm)');axes[1].grid(alpha=.3)
    fig.tight_layout();fig.savefig(out/'equilibrium_sweep.png',dpi=180);plt.close(fig)
    print(out)


if __name__=='__main__':main()
