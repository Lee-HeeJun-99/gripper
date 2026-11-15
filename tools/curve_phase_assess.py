"""Separate aggregate,phase,space/history and physical gates;no hidden FAILs."""
import argparse
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import OUT,write_json,sha
from history_assess import comparison
from birth_assess import observables,same_physics
from curve_cycle_loss import sample
from trial_validation import read_states


def physical_xml(path):
    root=ET.parse(path/'scene.scn').getroot();root.attrib.pop('dt',None)
    for e in list(root):
        if e.tag=='RequiredPlugin'or'AnimationLoop'in e.tag:root.remove(e)
    for e in root.iter():e.attrib.pop('filename',None)
    return ET.tostring(root)


def hardware(path):
    c=json.loads((path/'config.json').read_text());n=c['nodes'];body=ET.parse(path/'scene.scn').getroot().find('Node');result=[]
    for e in body.findall('FrameLayerNetwork'):
        result.append((e.tag,[int(i)*float(e.get('length'))/(n-1)for i in e.get('connectorIndices').split()],{k:v for k,v in e.attrib.items()if k not in('name','filename','stride','nodesPerLayer','startIndex','connectorIndices')}))
    for e in body.findall('RoutedCable'):
        result.append((e.tag,[(int(i)//n,int(i)%n*100/(n-1))for i in e.get('route').split()],{k:v for k,v in e.attrib.items()if k not in('name','route')}))
    return result


def relative(a,b,limit):
    r=abs(a-b)/abs(b)if b else(0. if a==0 else None)
    return dict(coarse=a,fine=b,absolute=abs(a-b),relative=r,status='PASS'if r is not None and r<=limit else'FAIL',limit=limit)


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',default='v1');a=p.parse_args()
    if not a.checkpoint.isalnum():raise ValueError('simple immutable checkpoint')
    target=OUT/('qualification_'+a.checkpoint+'.json')
    if target.exists():raise ValueError('refuse overwritten evidence')
    names=('full_coarse','full_fine','full_coarse_n41','full_coarse_history1250nm','full_coarse_repeat1');records={};paths={};checks={}
    for n in names:
        file=OUT/n/'metrics_same_grid_v2.json'
        if not file.exists():file=OUT/n/'metrics.json'
        if file.exists():records[n]=json.loads(file.read_text());paths[n]=file
    points=(0,.5,2,3,4,6,7,14,15,16,16.5,18,24)
    for left,right,limit in(('full_coarse','full_fine',.001),('full_coarse','full_coarse_n41',.01),('full_coarse','full_coarse_history1250nm',.01),('full_coarse','full_coarse_repeat1',1e-6)):
        key=left+'_'+right
        if left not in records or right not in records:checks[key]=dict(status='NOT RUN',reason='actual full result not yet present');continue
        u,v=records[left],records[right];same_physics(u,v)
        if any('hold_displacement_mm'not in q for q in(u,v)):
            checks[key]=dict(status='FAIL',reason='actual physical assessment unavailable;inspect retained comparator/engine failure');continue
        for field in('curved','event_grid','structural_compensation'):
            if u['identity'][field]!=v['identity'][field]:raise ValueError('compiled component changed '+field)
        if u['config']['time_grid']['event_times']!=v['config']['time_grid']['event_times']or u['config']['time_grid']['step_divisors']!=v['config']['time_grid']['step_divisors']:raise ValueError('different numerical policy')
        if hardware(OUT/left)!=hardware(OUT/right):raise ValueError('physical hardware changes')
        if right=='full_fine'and physical_xml(OUT/left)!=physical_xml(OUT/right):raise ValueError('physics XML changes with time grid')
        r=comparison(u,v,limit);r['motion_status']=r['status'];r['physical_hold_and_recovery']=bool(u['bounded_hold_pass']and v['bounded_hold_pass']and u['recovery_pass']and v['recovery_pass']);x,y=observables(OUT/left),observables(OUT/right)
        r['same_hold_observables']={k:relative(x[k],y[k],limit)for k in x};r['full_cycle_contact_loss']=relative(u['friction_dissipation'],v['friction_dissipation'],limit)
        a0={t:sample(OUT/left,t)['total']for t in points};b0={t:sample(OUT/right,t)['total']for t in points}
        r['phase_loss']={str(start)+'_'+str(end):relative(a0[end]-a0[start],b0[end]-b0[start],limit)for start,end in zip(points[:-1],points[1:])}
        r['aggregate_status']='PASS'if r['motion_status']=='PASS'and r['physical_hold_and_recovery']and r['full_cycle_contact_loss']['status']=='PASS'else'FAIL'
        r['phase_status']='PASS'if all(q['status']=='PASS'for q in r['phase_loss'].values())else'FAIL'
        r['status']='PASS'if r['aggregate_status']=='PASS'and r['phase_status']=='PASS'else'FAIL';checks[key]=r
    repetition={}
    if'full_coarse_repeat1'in records:
        x=read_states(OUT/'full_coarse/state.txt');y=read_states(OUT/'full_coarse_repeat1/state.txt')
        if len(x)!=len(y):raise ValueError('repeat actual frame count')
        repetition={k:float(np.max(np.abs(np.array([r[k]for r in x])-np.array([r[k]for r in y]))))for k in('X','V','R')}
    write_json(target,dict(status='EXPERIMENTAL',checks=checks,repeat_actual_state_errors=repetition,cases={n:{k:r.get(k)for k in('status','bounded_hold_pass','recovery_pass','global_force_residual','global_moment_residual','hold_displacement_mm','hold_rotation_increment_rad','friction_dissipation','process')}for n,r in records.items()},metrics_hashes={n:dict(path=str(paths[n]),sha256=sha(paths[n]))for n in records},global_energy='BLOCKED pending NEW grid journal',full_grasp_optimization='BLOCKED',scope='same physics;full-cycle AND small phase loss both retained. Aggregate PASS does NOT hide phase FAIL. Joint material sampling/history refinement,not a legacy Gauss knob. Existing uniform-grid FAILs remain unchanged.'))
    print({n:(r['status'],r.get('aggregate_status'),r.get('phase_status'),r.get('full_cycle_contact_loss',{}).get('relative'))for n,r in checks.items()})


if __name__=='__main__':main()
