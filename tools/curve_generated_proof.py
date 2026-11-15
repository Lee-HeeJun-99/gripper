"""Bind frozen generated diagnostic classes to exact physical source snapshots."""
import argparse
import hashlib
import json
import shutil
from curve_common import ROOT,OUT,BUILD,FRAME,sha,write_json


def digest(text):return hashlib.sha256(text.encode()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--version',default='v15');a=p.parse_args()
    if not a.version.isalnum():raise ValueError('simple immutable version')
    build=ROOT/'build/autonomous_20261116_curve_a01'/('transaction_fast_'+a.version);manifest=json.loads((build/'journal_manifest.json').read_text());out=OUT/('generated_'+a.version+'_proof');out.mkdir(exist_ok=False)
    common=(BUILD/'material_template/birth_template/legacy/Integrated.inc').read_text();common=common[:common.index('extern "C"')]
    curve=(BUILD/'CurvedGenerated.inc').read_text();curve=curve[:curve.index('extern "C"')].replace('#include "StickBase.inc"','#include "IntegratedClassOnly.inc"')
    frame=ROOT/'models/closure_frame/FrameLayer.cpp'
    if sha(frame)!=manifest['sources'][str(frame.relative_to(ROOT))]:raise ValueError('frame source differs from compiled snapshot')
    text=frame.read_text();text=text[:text.index('extern "C"')].replace('#include "AdaptiveBase.inc"','#include "IntegratedClassOnly.inc"')
    expected={'IntegratedClassOnly.inc':common,'CurveClassOnly.inc':curve,'FrameClassOnly.inc':text};checks={}
    for name,value in expected.items():
        actual=build/'normal_bridge'/name;checks[name]=dict(actual_sha256=sha(actual),expected_sha256=digest(value),equal=actual.read_text()==value)
        shutil.copy2(actual,out/name)
    class_proof={};actual=(FRAME.parent/'Integrated.inc').read_text()
    for name,end in(('EnergyField','LayerNetwork'),('RoutedCable','AnalyticContact')):
        x=common[common.index('class '+name):common.index('class '+end)];y=actual[actual.index('class '+name):actual.index('class '+end)]
        class_proof[name]=dict(equal=x==y,sha256=digest(y))
    declared=json.loads((build/'normal_bridge/ClassIdentity.json').read_text())
    passed=all(c['equal']for c in checks.values())and all(c['equal']and declared[n]==c['sha256']for n,c in class_proof.items())and declared['identical_frozen_class_definitions']
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',generated=checks,physical_and_diagnostic_class_identity=class_proof,compiled_manifest_sha256=sha(build/'journal_manifest.json'),compiled_binaries=manifest['binaries'],scope='exact frozen source generation/ABI class-definition identity,not a physics pass;no old manifest/binary overwritten'))
    print(passed,checks,class_proof)


if __name__=='__main__':main()
