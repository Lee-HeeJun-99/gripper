"""Same-binary OFF/ON local-coordinate recorder purity at a prescribed state."""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case)
    summary=json.loads((source/'summary.json').read_text())
    if summary.get('status')!='PASS' or not summary.get('finite') or not (source/'1/displacement.csv').exists():raise RuntimeError('complete enabled-recorder source required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    tree=ET.parse(source/'1/scene.scn')
    for node in tree.iter():
        for key,value in list(node.attrib.items()):node.set(key,value.replace(str(source/'1'),str(out)))
    tree.find("Node[@name='assembly']/FilmRailTendon").set('displacementFilename','')
    tree.write(out/'scene.scn')
    command=json.loads((source/'1/process/command.json').read_text());command[-1]=str(out/'scene.scn')
    result=guarded(command,out/'process',120)
    files=('journal.csv','contact.csv','momentum.csv','contact_rows.csv','coupled.csv')
    identical={name:(out/name).is_file() and sha(out/name)==sha(source/'1'/name) for name in files}
    rows=list(csv.DictReader((out/'journal.csv').open())) if (out/'journal.csv').exists() else []
    ok=result['exit_code']==0 and len(rows)==summary['rows'] and all(identical.values())
    write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='actual same-binary recorder purity;NOT contact/whole energy qualification',
        physical_csv_identical=identical,process=result,script_sha256=sha(__file__),source_identity_sha256=sha(source/'identity.json'),
        input_coordinate_journal_sha256=sha(source/'1/displacement.csv')))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',physical_csv_identical=identical)))
if __name__=='__main__':main()
