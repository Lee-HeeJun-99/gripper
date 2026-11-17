"""Actual negative model guards and same-binary accepted-state replay identity."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--compare');a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    source=ROOT/'results'/('autonomous_film_'+a.case);identity=json.loads((source/'identity.json').read_text())
    original=source/'supplied_film_event';stages={}
    for name,reason in (('extra_mass','event prototype rejects additional body mass'),('moving_object','event prototype rejects moving/dynamic other bodies')):
        target=out/name;target.mkdir();tree=ET.parse(original/'scene.scn');root=tree.getroot()
        for e in root.iter():
            for key,value in list(e.attrib.items()):
                if str(original) in value:e.set(key,value.replace(str(original),str(target)))
        plugin=next(Path(e.get('pluginName')) for e in root.findall('RequiredPlugin') if e.get('pluginName','').endswith('libReGripImpactReference.so'))
        if sha(plugin)!=identity['binary_sha256']:raise ValueError('compiled event binary changed')
        if name=='extra_mass':
            child=ET.SubElement(root,'Node',name='unsupported_extra_body');ET.SubElement(child,'MechanicalObject',template='Vec3d',position='1000 0 0');ET.SubElement(child,'UniformMass',totalMass='1')
        else:root.find("Node[@name='fixed']/SphereCollisionModel").set('moving','1')
        path=target/'scene.scn';tree.write(path)
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',path],target/'process',30)
        log=(target/'process/stdout.log').read_text()+(target/'process/stderr.log').read_text()
        stages[name]=dict(status='PASS' if process['exit_code']!=0 and reason in log else 'FAIL',scope='expected invalid model rejected;NOT a physical PASS',process=process,expected_reason=reason)
    equal={}
    if a.compare:
        other=ROOT/'results'/('autonomous_film_'+a.compare)
        for directory in source.glob('film_sequence_*'):
            for name in ('event.csv','event.csv.endpoint.csv','journal.csv','displacement.csv'):
                left=directory/name;right=other/directory.name/name
                if not right.exists():raise ValueError('complete shared cases required')
                equal[directory.name+'/'+name]=dict(equal=sha(left)==sha(right),left_sha256=sha(left),right_sha256=sha(right))
    result=dict(status='PASS' if all(s['status']=='PASS' for s in stages.values()) and all(s['equal'] for s in equal.values()) else 'FAIL',scope='negative guards and accepted-journal byte identity only;NOT full time/physical energy certification',stages=stages,identity=equal,script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],guards={k:v['status'] for k,v in stages.items()},identity_records=len(equal),all_equal=all(s['equal'] for s in equal.values()))))
if __name__=='__main__':main()
