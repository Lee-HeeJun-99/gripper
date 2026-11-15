"""Separate2/4/8-layer actual SOFA structure; no compensated updates assumed."""
import json,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import asdict
from beam_common import ROOT,OUT,SDK,PLUGIN,FRAME,identity,material,sha,write_json
from integrated_trial import Config,scene,analyze,sequence
from run_trial import execute_process
def run(name,c):
    out=OUT/'multilayer'/name;out.mkdir(parents=True,exist_ok=False);g=scene(out,c);tree=ET.parse(out/'scene.scn');root=tree.getroot();root.find('EulerImplicitSolver').set('rayleighMass','2');body=root.find('Node');beam=body.find('BeamFEMForceField');i=list(body).index(beam);body.remove(beam);edges=[j for l in range(c.layers) for n in range(c.nodes-1) for j in (l*c.nodes+n,l*c.nodes+n+1)];m=material()
    if c.equal_total_material:
        ratio=2/c.layers;m={k:v*(ratio if k in ('EA','GAy','GAz') else ratio*ratio) for k,v in m.items()}
    body.insert(i,ET.Element('ConservativeBeam',name='new_beam',edges=sequence(edges),**{k:str(v) for k,v in m.items()}));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);cmd=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(c.validate()),'0',str(FRAME),str(PLUGIN)];write_json(out/'config.json',dict(**asdict(c),rayleigh_mass=2,beam_material=m));write_json(out/'command.json',cmd);r=dict(config=asdict(c),identity=identity());p=execute_process(cmd,out,480);r['process']=p
    try:r.update(analyze(out,c,g,p,(out/'stdout.log').read_text()+(out/'stderr.log').read_text()))
    except (ValueError,OSError,KeyError) as e:r.update(status='FAIL',failure_reason=str(e))
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'metrics.json',r);print(name,r.get('status'),r.get('relative_residual'),r.get('tip_deflection_mm'),p['runtime_s'],flush=True);return r
def main():
    cases=[(f'L{l}_k{k}',Config(layers=l,k=k,load=1e-6,duration=12.)) for l in (2,4,8) for k in (0,100)]
    results={};write_json(OUT/'multilayer_plan.json',dict(cases=[dict(name=n,config=asdict(c)) for n,c in cases],maximum_children=2,wall_cap=480,compensated_positions=False))
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,n,c):n for n,c in cases}
        for f in as_completed(tasks):
            n=tasks[f]
            try:results[n]=f.result()
            except Exception as e:results[n]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'multilayer_campaign.json',results)
if __name__=='__main__':main()
