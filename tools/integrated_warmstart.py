"""Independent-FEM-seeded SOFA static solves. Original rest geometry is preserved.

Not a replacement for cold transient convergence. No tolerance/load relaxation.
Measured deflection is relative to original rest geometry, NOT the seed position.
"""
from dataclasses import replace,asdict
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from models.multilayer.beam import Design,solve
from integrated_trial import Config,scene,analyze,sequence,geometry
from integrated_common import ROOT,SOFA,OUT,BUILD,write_json,sha,provenance
from run_trial import execute_process

def main():
    root=OUT/'warmstart';root.mkdir(parents=True,exist_ok=False);results={};d=Config(layers=8,k=100)
    cases=[('L4_control',replace(d,layers=4)),('L8_base',d),('L8_halfdt',replace(d,dt=.00025)),('L8_mesh',replace(d,nodes=21,connectors=tuple(range(2,21,2))))]
    cases += [(f'equal_material_L{L}_k{k}',replace(d,layers=L,k=k,equal_total_material=True)) for L in (4,8) for k in (0,100)]
    for name,c in cases:
        out=root/name;out.mkdir();g=scene(out,c);r,A,I,h=geometry(c)
        reference=solve(Design(length=c.length,nodes=c.nodes,layers=c.layers,coupling=c.k,connectors=tuple(c.connectors) or tuple(range(1,c.nodes)),area=A,inertia=I,thickness=h,load=c.load))
        q=reference['displacement'];tree=ET.parse(out/'scene.scn');obj=tree.getroot().find('.//MechanicalObject');rest=list(map(float,obj.get('position').split()));position=rest.copy()
        for i in range(c.layers*c.nodes):
            position[7*i]+=q[3*i];position[7*i+2]+=q[3*i+1];position[7*i+4]=math.sin(-q[3*i+2]/2);position[7*i+6]=math.cos(-q[3*i+2]/2)
        obj.set('rest_position',sequence(rest));obj.set('position',sequence(position));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
        plugin=BUILD/'plugin/libReGripIntegrated.so';cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(c.duration/c.dt)),'--hideProgressBar','-l',str(plugin),str(out/'scene.scn')]
        config=dict(**asdict(c),initialization='independent linear FEM displacement/rotation; original rest_position preserved')
        write_json(out/'config.json',config);write_json(out/'seed.json',reference);write_json(out/'command.json',cmd)
        p=execute_process(cmd,out,180);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();result=dict(config=config,provenance=provenance(),binary_sha256=sha(plugin),process=p,scope='SOFA measured equilibrium from independent static seed, NOT cold transient or golden replay')
        try:
            result.update(analyze(out,c,g,p,log,rest_reference=rest));result['FEM_relative_error']=abs(result['tip_deflection_mm']/reference['deflection_mm']-1)
        except (ValueError,KeyError,OSError) as e:result.update(status='FAIL',reason=str(e))
        result['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'};write_json(out/'metrics.json',result);results[name]=result;write_json(root/'summary.json',results)
        print(name,result['status'],result.get('tip_deflection_mm'),result.get('relative_residual'),flush=True)

if __name__=='__main__':main()
