import argparse,json,xml.etree.ElementTree as ET
import beam_grasp_trial as base
from history_trial import analyze
from birth_monitor import Monitor
from run_trial import execute_process
from curve_common import OUT,SDK,FRAME,BEAM,PLUGIN,identity,sha,write_json
def run(name,history=.0025,nodes=11,dt=.0005,duration=18,profile=False,wall=480,fixed_layout=False,fixed_connectors=False,fixed_cables=False):
    ident=identity();base.OUT=OUT;out=base.run(name,nodes=nodes,history=history,dt=dt,duration=24 if profile else duration,prepare_only=True);tree=ET.parse(out/'scene.scn');contact=tree.getroot().find('Node').find('ActiveIntervalContact');contact.tag='CurvedMaterialContact';tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    if fixed_layout or fixed_connectors or fixed_cables:
        factor=(nodes-1)//10;body=tree.getroot().find('Node')
        if fixed_layout or fixed_connectors:
            for layer in body.findall('FrameLayerNetwork'):layer.set('connectorIndices',' '.join(str(i*factor)for i in range(1,11)))
        if fixed_layout or fixed_cables:
            for layer,cable in enumerate(body.findall('RoutedCable')):cable.set('route',' '.join(str(layer*nodes+i*factor)for i in range(11)))
        tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    policy='fixed_10mm_material_connectors_and_cable_guides'if fixed_layout else'fixed_connectors_only'if fixed_connectors else'fixed_cable_guides_only'if fixed_cables else'all_mesh_nodes_inherited_layout'
    config=json.loads((out/'config.json').read_text());config.update(duration=4 if profile else duration,profile_only=profile,contact_model='director_Hermite_spatial_virtual_work',tangent_quadrature='immutable material midpoints',normal_quadrature='same immutable material midpoints',history_model='fixed material points no remapping',samples=8,layout_policy=policy)
    steps=round(config['duration']/dt);command=list(map(str,[SDK/'bin/graph_probe',SDK,out/'scene.scn',steps,0,FRAME,BEAM,PLUGIN]));write_json(out/'command.json',command);write_json(out/'config.json',config);write_json(out/'identity.json',ident);monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process)
    if profile:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();result=dict(status='EXPERIMENTAL'if process['exit_code']==0 and'[ERROR]'not in log and f'{steps} iterations done'in log else'FAIL',process=process,config=config,identity=ident,scope='4s runtime profile only')
    else:result=analyze(out,config,process)
    result['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()};write_json(out/'metrics.json',result);print(name,result['status'],process['runtime_s'],result.get('hold_displacement_mm'),flush=True);return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--history',type=float,default=.0025);p.add_argument('--nodes',type=int,default=11);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--duration',type=float,default=18);p.add_argument('--profile',action='store_true');p.add_argument('--fixed-layout',action='store_true');a=p.parse_args();run(a.name,history=a.history,nodes=a.nodes,dt=a.dt,duration=a.duration,profile=a.profile,fixed_layout=a.fixed_layout)
