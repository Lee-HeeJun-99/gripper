"""Keep prefix convergence separate from physical equilibrium/full-cycle gates."""
import argparse
import json
import xml.etree.ElementTree as ET
from curve_common import OUT,sha,write_json
from curve_cycle_loss import sample
from curve_phase_assess import relative


def normalized(path):
    root=ET.parse(path/'scene.scn').getroot()
    for element in root.iter():
        element.attrib.pop('filename',None)
        if element.tag in ('CurvedMaterialContact','PatchRefinedContact'):
            element.tag='SAME_VERIFIED_CONSTITUTIVE_SOURCE'
            element.attrib.pop('edgeSpacing',None)
            element.attrib.pop('historySpacing',None)
    return ET.tostring(root)


def main():
    p=argparse.ArgumentParser();p.add_argument('--version',default='v1');a=p.parse_args()
    if not a.version.isalnum():raise ValueError('simple evidence version')
    target=OUT/'patch_refinement'/('prefix_assessment_'+a.version+'.json')
    if target.exists():raise ValueError('immutable evidence exists')
    parent=OUT/'full_coarse_history1250nm';paths={'uniform1250nm':parent,'uniform1000nm':OUT/'history1000nm_prefix82_v1','local625nm':OUT/'patch_refinement/local625_prefix82','local312nm':OUT/'patch_refinement/local312_prefix82'}
    losses={};missing={};hashes={};times=(0,.5,2,3,4,6,7,8.2)
    for name,path in paths.items():
        summary=path/'summary.json'
        if name!='uniform1250nm':
            if not summary.exists():missing[name]='NOT RUN';continue
            decision=json.loads(summary.read_text())
            if decision['status']!='PASS':missing[name]=decision['status'];continue
        if normalized(path)!=normalized(parent):raise ValueError('unintended physical/control/time-grid XML change')
        cumulative={t:sample(path,t)['total']for t in times}
        losses[name]={f'{lo}_{hi}':cumulative[hi]-cumulative[lo]for lo,hi in zip(times[:-1],times[1:])}
        hashes[name]={f:sha(path/f)for f in('scene.scn','contact.csv')}
    checks={}
    for first,second in(('uniform1250nm','uniform1000nm'),('uniform1250nm','local625nm'),('local625nm','local312nm')):
        key=first+'_'+second
        if first not in losses or second not in losses:checks[key]=dict(status='NOT RUN',reason='actual completed prefix prerequisite missing');continue
        phases={key:relative(value,losses[second][key],.01)for key,value in losses[first].items()}
        checks[key]=dict(status='PASS'if all(v['status']=='PASS'for v in phases.values())else'FAIL',phases=phases)
    write_json(target,dict(status='EXPERIMENTAL',checks=checks,raw_phase_losses_Fmm=losses,missing=missing,source_hashes=hashes,scope='same actual cold-start grid/load/material law;JOINT normal/tangent quadrature and material-history refinement.1percent retained. Prefix8.2s cannot qualify late pressure/release,full energy,mesh/dt or12wrench grasp. Local refinement is nested1250->625->312 ONLY in90--100mm;uniform1000nm is a separate contrast.'))
    print({k:v['status']for k,v in checks.items()})


if __name__=='__main__':main()
