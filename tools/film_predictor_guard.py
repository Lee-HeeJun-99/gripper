"""Actual negative SOFA test: predictor mode cannot publish without full owner."""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    previous=ROOT/'results'/('autonomous_film_'+a.case)
    identity=json.loads((previous/'identity.json').read_text())
    if not identity.get('single_newton_predictor') or json.loads((previous/'summary.json').read_text())['status']!='PASS':
        raise RuntimeError('complete qualified predictor execution required as guard source')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    tree=ET.parse(previous/'1/scene.scn')
    for node in tree.iter():
        for key,value in list(node.attrib.items()):
            node.set(key,value.replace(str(previous/'1'),str(out)))
    tree.find('FilmNativeCoupledCorrection').set('completeFreeStage','0')
    tree.write(out/'scene.scn')
    command=json.loads((previous/'1/process/command.json').read_text())
    command[command.index('-n')+1]='1';command[-1]=str(out/'scene.scn')
    result=guarded(command,out/'process',60)
    text=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
    journal=out/'journal.csv'
    rows=list(csv.DictReader(journal.open())) if journal.exists() else []
    expected='predictor-only mode requires coupled.completeFreeStage=1'
    ok=result['exit_code']!=0 and expected in text and not rows
    write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='negative safety guard,NOT physics convergence',
        expected_rejection=expected,actual_accepted_rows=len(rows),process=result,
        source_scene_sha256=sha(previous/'1/scene.scn'),test_scene_sha256=sha(out/'scene.scn'),
        script_sha256=sha(__file__),source_identity_sha256=sha(previous/'identity.json')))
    print(json.dumps(dict(guard_status='PASS' if ok else 'FAIL',accepted_rows=len(rows),exit_code=result['exit_code'])))

if __name__=='__main__':main()
