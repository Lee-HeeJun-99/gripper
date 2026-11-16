"""Three alternating same-binary endpoint-search pairs;not physics approval."""
import argparse,csv,json,math,statistics,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);summary=json.loads((source/'summary.json').read_text())
    if summary.get('status')!='PASS' or not summary.get('finite'):raise ValueError('complete source required')
    cmd=json.loads((source/'1/process/command.json').read_text());count=int(cmd[cmd.index('-n')+1])
    if count>40:raise ValueError('bounded short benchmark only')
    original=ET.parse(source/'1/scene.scn');owner=original.find('FilmNativeCoupledCorrection')
    if owner.get('candidateComplete')!='1' or owner.get('candidateBroadPhase')!='0':raise ValueError('explicit broadphase-disabled candidate baseline required')
    identity=json.loads((source/'identity.json').read_text());binaries={}
    for n in original.findall('RequiredPlugin'):
        path=Path(n.get('pluginName',''))
        if path.name in ('libReGripFilmShell.so','libReGripFilmRailTendon.so','libReGripFilmNativeObserver.so'):binaries[str(path)]=sha(path)
    if len(binaries)!=3:raise ValueError('all three actual plugin identities required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);records=[]
    journals=('journal.csv','contact.csv','contact_rows.csv','momentum.csv','coupled.csv')
    reference={name:sha(source/'1'/name) for name in journals}
    for i,enabled in enumerate([False,True]*3):
        case=out/str(i);case.mkdir();tree=ET.parse(source/'1/scene.scn')
        for node in tree.getroot().iter():
            for key,value in list(node.attrib.items()):node.set(key,value.replace(str(source/'1'),str(case)))
        tree.find('FilmNativeCoupledCorrection').set('candidateBroadPhase','1' if enabled else '0');tree.write(case/'scene.scn')
        command=cmd.copy();command[-1]=str(case/'scene.scn')
        if any(sha(Path(path))!=value for path,value in binaries.items()):raise ValueError('binary drift')
        process=guarded(command,case/'process',480)
        log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
        rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
        finite=bool(rows) and all(math.isfinite(float(v)) for r in rows for k,v in r.items() if k!='x') and all(math.isfinite(float(v)) for r in rows for v in r['x'].split())
        complete=process['exit_code']==0 and len(rows)==count and finite and not any(s in log for s in ('[ERROR]','Unused Attribute','Newton-Raphson method failed to converge'))
        equal=complete and all(sha(case/name)==reference[name] for name in journals)
        records.append(dict(broadphase=enabled,process=process,complete=complete,physical_journals_bitwise_identical=equal))
        if not equal:break
    ratios=[records[i+1]['process']['runtime_s']/records[i]['process']['runtime_s'] for i in range(0,len(records)-1,2)]
    equality=len(records)==6 and all(r['physical_journals_bitwise_identical'] for r in records);median=statistics.median(ratios) if ratios else None
    result=dict(status='PASS' if equality and median<1 else 'FAIL',physical_identity='PASS' if equality else 'FAIL',scope='short same-binary cost contrast only;NOT general speed or physics certification',records=records,pair_ratios=ratios,median_ratio=median,reference_journals=reference,binaries=binaries,source_case=a.case,source_identity_sha256=sha(source/'identity.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','physical_identity','pair_ratios','median_ratio')}))
if __name__=='__main__':main()
