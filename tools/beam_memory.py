"""New conservative3finger memory scope, not re-labelled prior minimal evidence."""
import json,xml.etree.ElementTree as ET
from beam_common import ROOT,OUT,BUILD,PREFIX,SDK,FRAME,PLUGIN,sha,write_json,identity
from closure_validation_suite import logged
from run_trial import execute_process
def main():
    out=OUT/'memory';out.mkdir(exist_ok=False);build=BUILD/'memory_diagnostics'
    for name,cmd in [('configure',['cmake','-S','diagnostics/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(build),'--target','beam_memory','-j2'])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='BLOCKED',result=r));return
    scenes=[]
    for cycle in range(2):
        d=out/str(cycle);d.mkdir();tree=ET.parse(OUT/'grasp/Tz_v2/scene.scn');body=tree.getroot().find('Node')
        for e in list(body):
            if e.tag=='IntegratedRecorder':body.remove(e);continue
            if 'filename' in e.attrib:e.set('filename',str(d/e.get('filename').rsplit('/',1)[-1]))
            if e.tag in ('ActiveIntervalContact','FrameLayerNetwork'):e.set('stride','60000')
        tree.write(d/'scene.scn',encoding='utf-8',xml_declaration=True);scenes.append(d/'scene.scn')
    cmd=[str(build/'beam_memory'),str(SDK),*map(str,scenes),str(FRAME),str(PLUGIN)];write_json(out/'command.json',cmd);write_json(out/'identity.json',identity());p=execute_process(cmd,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();rows=[json.loads(s[7:]) for s in log.splitlines() if s.startswith('MEMORY ')];graphs=[json.loads(s[6:]) for s in log.splitlines() if s.startswith('GRAPH ')];growth=[]
    for cycle in range(2):
        tail=[r for r in rows if r['cycle']==cycle and r['phase']=='animated' and r['step']>=30000]
        if len(tail)==4:growth.append(tail[-1]['live_heap']-tail[0]['live_heap'])
    unloaded=[r for r in rows if r['phase']=='unloaded'];loaded=[r for r in rows if r['phase']!='unloaded'];checks=dict(execution=p['exit_code']==0 and '[ERROR]' not in log,two_cycles=len(unloaded)==2 and len(growth)==2,live_plateau=len(growth)==2 and max(growth)<1024**2,loaded_fd_stable=bool(loaded) and len(set(r['fds'] for r in loaded))==1,unloaded_fd_stable=len(unloaded)==2 and unloaded[0]['fds']==unloaded[1]['fds'],graph_released=len(graphs)==2 and all(r['retained']==0 for r in graphs));result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,process=p,rows=rows,graphs=graphs,last30000_live_growth=growth,scope='newbeam+sixlayers+threecablespairs+pressure+friction+freeobject;two60000step reloads,sameprocess total120000,not240000single-runorhours; observer stride changed forI/O only,physics sequence identical');write_json(out/'summary.json',result);print(result)
if __name__=='__main__':main()
