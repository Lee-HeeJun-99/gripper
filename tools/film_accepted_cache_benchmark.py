"""Alternating SAME-BINARY actual SOFA test of an opt-in within-step cache."""
import argparse
import csv
import json
import math
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--pairs',type=int,default=3);a=p.parse_args()
    if not 1<=a.pairs<=3:raise ValueError('finite alternating benchmark budget')
    source=ROOT/'results'/('autonomous_film_'+a.case)
    reference=json.loads((source/'summary.json').read_text())
    if reference.get('status')!='PASS' or not reference.get('finite'):raise RuntimeError('completed actual source required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    command=json.loads((source/'1/process/command.json').read_text());steps=int(command[command.index('-n')+1])
    if steps>100:raise ValueError('benchmark only after100-step-or-shorter profiling')
    base_tree=ET.parse(source/'1/scene.scn')
    binaries={str(Path(n.get('pluginName'))):sha(Path(n.get('pluginName'))) for n in base_tree.findall('RequiredPlugin') if n.get('pluginName','').startswith('/')}
    runs=[];metrics=('journal.csv','contact.csv','momentum.csv','contact_rows.csv','coupled.csv')
    hashes=[{name:sha(source/'1'/name) for name in metrics}]
    for pair in range(a.pairs):
        for enabled in ((False,True) if pair%2==0 else (True,False)):
            directory=out/(str(pair)+('_cache' if enabled else '_base'));directory.mkdir()
            tree=ET.parse(source/'1/scene.scn')
            for node in tree.iter():
                for key,value in list(node.attrib.items()):node.set(key,value.replace(str(source/'1'),str(directory)))
            tree.find('FilmNativeCoupledCorrection').set('reuseAcceptedEvaluation','1' if enabled else '0')
            tree.write(directory/'scene.scn')
            if any(sha(Path(name))!=expected for name,expected in binaries.items()):raise RuntimeError('benchmark binary drift')
            trial=command.copy();trial[-1]=str(directory/'scene.scn');process=guarded(trial,directory/'process',480)
            journal=directory/'journal.csv';rows=list(csv.DictReader(journal.open())) if journal.exists() else []
            finite=all(math.isfinite(float(value)) for row in rows for key,value in row.items() if key!='x') and all(math.isfinite(float(value)) for row in rows for value in row['x'].split())
            complete=process['exit_code']==0 and len(rows)==steps and finite
            run=dict(pair=pair,cache=enabled,process=process,complete=complete,scene_sha256=sha(directory/'scene.scn'))
            if complete:
                run['physical_csv_hashes']={name:sha(directory/name) for name in metrics}
                hashes.append(run['physical_csv_hashes'])
                trace=(directory/'coupled.csv.newton.log').read_text().splitlines()
                counts=[line.split() for line in trace if line.startswith('mechanical_evaluations ')]
                run.update(mechanical_evaluations=sum(int(line[1]) for line in counts),accepted_reuses=sum(int(line[3]) for line in counts))
            runs.append(run);write_json(out/'progress.json',dict(runs=runs,binaries=binaries))
            if not complete:break
        if not runs[-1]['complete']:break
    complete=len(runs)==2*a.pairs and all(run['complete'] for run in runs)
    identical=complete and all(item==hashes[0] for item in hashes)
    ratios=[]
    if complete:
        for pair in range(a.pairs):
            old=next(r for r in runs if r['pair']==pair and not r['cache']);new=next(r for r in runs if r['pair']==pair and r['cache'])
            ratios.append(new['process']['runtime_s']/old['process']['runtime_s'])
    ratio=statistics.median(ratios) if ratios else None
    ok=identical and ratio is not None and ratio<1
    write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='same-binary cache qualification;NOT time/contact/grasp certification',
        physically_identical_csv=identical,median_runtime_ratio=ratio,pair_ratios=ratios,runs=runs,binaries=binaries,
        script_sha256=sha(__file__),source_identity_sha256=sha(source/'identity.json'),
        decision='ACCEPT scoped opt-in cache' if ok else 'REJECT optimization or investigate failed execution/identity'))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',physical_csv_identical=identical,median_runtime_ratio=ratio)))

if __name__=='__main__':main()
