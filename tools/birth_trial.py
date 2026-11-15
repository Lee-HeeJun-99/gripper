import argparse,json,xml.etree.ElementTree as ET
import beam_grasp_trial as base
from history_trial import analyze
from birth_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,identity,write_json,sha
from run_trial import execute_process
def run(name,nodes=11,samples=8,history=.01,dt=.0005,duration=24,cell_order=2,profile=False,wall=480,journal=False):
    ident=identity();base.OUT=OUT;out=base.run(name,nodes=nodes,samples=samples,history=history,dt=dt,duration=24 if profile else duration,prepare_only=True)
    tree=ET.parse(out/'scene.scn');field=tree.getroot().find('Node').find('ActiveIntervalContact');field.tag='BirthAwareContact';field.set('cellOrder',str(cell_order));
    if journal:field.set('journalFilename',str(out/'energy_journal.csv'))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);c=json.loads((out/'config.json').read_text());c.update(duration=4 if profile else duration,contact_model='birth_material_chord_implicit_derivative',normal_quadrature=samples,tangent_cell_order=cell_order,profile_only=profile,journal=journal)
    steps=round(c['duration']/dt);command=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(FRAME),str(BEAM),str(PLUGIN)];write_json(out/'command.json',command);write_json(out/'config.json',c);write_json(out/'identity.json',ident)
    p=execute_process(command,out,wall);write_json(out/'execution_result.json',p)
    if profile:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(status='EXPERIMENTAL' if p['exit_code']==0 and '[ERROR]' not in log and f'{steps} iterations done' in log else 'FAIL',config=c,identity=ident,process=p,scope='4s profile, not equilibrium',predicted_18s_wall=p['runtime_s']*4.5)
    else:r=analyze(out,c,p)
    r['artifacts']={f.name:sha(f) for f in out.iterdir() if f.is_file()};write_json(out/'metrics.json',r);print(name,r['status'],p['runtime_s'],r.get('hold_displacement_mm'),flush=True);return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--nodes',type=int,default=11);p.add_argument('--samples',type=int,default=8);p.add_argument('--history',type=float,default=.01);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--duration',type=float,default=24);p.add_argument('--cell-order',type=int,default=2);p.add_argument('--profile',action='store_true');p.add_argument('--journal',action='store_true');a=p.parse_args();run(a.name,nodes=a.nodes,samples=a.samples,history=a.history,dt=a.dt,duration=a.duration,cell_order=a.cell_order,profile=a.profile,journal=a.journal)
