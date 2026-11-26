"""Actual RevAF transmission topology fault screen, not measured failure data.

A bearing between input hub and drum is a parallel torque path. Its normal
drag and seizure behavior cannot disappear from a force-cap safety claim.
"""
import argparse,json,shutil
from baseline_registry import ROOT,ref,dump

def paths(edges,node='INPUT_HUB',target='DRUM',visited=()):
    if node==target:return [[]]
    result=[]
    for edge in edges:
        if edge['from']==node and edge['to'] not in visited+(node,):
            result.extend([[edge]+tail for tail in paths(edges,edge['to'],target,visited+(node,))])
    return result

def unprotected(edges):
    return [p for p in paths(edges) if not any(e.get('guaranteed_limit') for e in p)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='revAF_layout6');a=p.parse_args()
    out=ROOT/'validation/overload'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text())
    required=['F0_CLUTCH_INPUT_HUB','F0_CLUTCH_BEARING','F0_DRUM']
    assert all(n in d['part_references'] for n in required)
    # Grant the friction route a PERFECT torque bound as a negative control:
    # even this generous counterfactual cannot protect a parallel bearing path.
    fixed_support='F0_CLUTCH_GROUND_SPINDLE' in d['part_references']
    if fixed_support:
        required+=['F0_CLUTCH_GROUND_SPINDLE','F0_CLUTCH_INNER_CLIP','F0_CLUTCH_GROUND_BOLT_88','F0_CLUTCH_GROUND_BOLT_132','F0_MOTOR_PLATE']
        assert d['torque_model']['faces']==1
    edges=[dict(id='friction_faces',**{'from':'INPUT_HUB','to':'DRUM'},guaranteed_limit=True,basis='COUNTERFACTUAL ideal calibrated friction cap; actual cap unqualified'),
           dict(id='support_bearing',**{'from':'GROUND' if fixed_support else 'INPUT_HUB','to':'DRUM'},guaranteed_limit=False,basis='Actual 688A inner ring on ground spindle' if fixed_support else 'Actual 8mm hub journal -> 688A inner ring -> rolling elements -> outer ring in drum. Drag/seizure bound unavailable.')]
    bypasses=unprotected(edges)
    assert (not bypasses) if fixed_support else (len(bypasses)==1 and bypasses[0][0]['id']=='support_bearing')
    assert not unprotected(edges[:1])
    grounded=[edges[0],dict(edges[1],**{'from':'GROUND'})]
    assert not unprotected(grounded)
    result=dict(status='BOUNDED_TOPOLOGY_SCREEN_PASS' if fixed_support else 'FORCE_CAP_TOPOLOGY_FAIL',scope='Actual support topology plus explicit bearing-seizure counterfactual; no actual hardware fault was induced',
        candidate=ref(src),producer=ref(out/'producer.py'),part_sources={n:d['part_references'][n] for n in required},edges=edges,
        bypasses=[[e['id'] for e in p] for p in bypasses],
        motor_reference_holding_torque_Nm=.45,nominal_drum_radius_m=.01125,
        illustrative_seizure_reference_tension_N=.45/.01125,
        warning=('Ground support removes this specific bearing bypass in the declared graph only; actual friction, other faults, structural capacity and protected maximum are still unqualified.' if fixed_support else '40N is a holding-torque reference, not measured jam load or certified motor maximum. Even an ideal friction cap does not eliminate this parallel path.'),
        digital_alternatives=['Support drum on a genuinely fixed-ground bearing/spindle; verify input shaft clearance and actual retention','Place a separately qualified overload disconnect upstream of every input/output path','Choose an actuator with a verified complete output torque/energy envelope and qualify the structure at that envelope'],
        controls=['ideal friction-only route is protected','adding actual input/output bearing exposes bypass','ground-supported bearing removes this input/output bypass in graph only'],
        product_force_cap_qualified=False,ground_supported_CAD_created=fixed_support,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
