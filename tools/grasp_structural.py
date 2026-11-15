"""Same8-layer cold problem, quarterdt; decimate observer only, wall cap300s."""
import xml.etree.ElementTree as ET
import argparse
from dataclasses import asdict
from integrated_trial import Config,scene,analyze
from grasp_common import ROOT,SOFA,OUT,write_json,sha,provenance
from run_trial import execute_process

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--patched',action='store_true');parser.add_argument('--dt',type=float,default=.000125);parser.add_argument('--name');args=parser.parse_args()
    out=OUT/'structural'/(args.name or ('quarterdt_patched' if args.patched else 'quarterdt'));out.mkdir(parents=True,exist_ok=False);c=Config(layers=8,k=100,dt=args.dt,duration=12,stride=round(.0125/args.dt));g=scene(out,c);tree=ET.parse(out/'scene.scn');root=tree.getroot();body=root.find('Node');old=ROOT/'build/stabilization_20261115';sdk=ROOT/'build/grasp_20261115/sofa_patched';plugins=[sdk/'lib/libReGripStabilization.so',sdk/'lib/libReGripCompensated.so'] if args.patched else [old/'plugin/libReGripStabilization.so',old/'compensated/libReGripCompensated.so']
    body.insert(0,ET.Element('CompensatedEulerPositions',excludedIndices=' '.join(map(str,g['fixed'])),filename=str(out/'compensation.csv')))
    ET.SubElement(body,'ForceAudit',filename=str(out/'forces.txt'),after='11.9',stride=str(c.stride));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(c.validate()),'--hideProgressBar']
    for plugin in plugins:command+=['-l',str(plugin)]
    command.append(str(out/'scene.scn'));write_json(out/'command.json',command);write_json(out/'config.json',asdict(c));record=dict(config=asdict(c),provenance=provenance(),binary_sha256={str(p.relative_to(ROOT)):sha(p) for p in plugins},scope='same structure/forces/dt; observer stride20→100 only, max wall180→300; tolerances unchanged')
    if args.patched:
        command=[str(sdk/'bin/graph_probe'),str(sdk),str(out/'scene.scn'),str(c.validate()),'0',*map(str,plugins)];write_json(out/'command.json',command);record['scope']='matched-source patched native engine; unchanged structural law/loads; sampling period.0125s; wall480s derived from prior measured throughput, not physical tolerance relaxation'
    p=execute_process(command,out,480 if args.patched else 300);record['process']=p
    try:record.update(analyze(out,c,g,p,(out/'stdout.log').read_text()+(out/'stderr.log').read_text()))
    except (ValueError,OSError,KeyError) as exc:record.update(status='FAIL',reason=str(exc))
    record['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'};write_json(out/'metrics.json',record);print(record.get('status'),record.get('relative_residual'),record.get('tip_deflection_mm'))

if __name__=='__main__':main()
