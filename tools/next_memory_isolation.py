"""Minimal native-engine controls to localize stepwise RSS growth, not a fix."""
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
from native_scene import generate
from next_headless_check import measured
from verification_common import ROOT,SOFA,write_json

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'results/next_phase/memory_isolation');a=parser.parse_args()
    root=a.out;root.mkdir(parents=True,exist_ok=False);cases={}
    for name in ('empty','mass_implicit','beam_explicit'):
        scene_dir=root/(name+'_scene');scene_dir.mkdir();generate(scene_dir/'scene.scn')
        tree=ET.parse(scene_dir/'scene.scn');node=tree.getroot()
        for parent in list(node.iter('Node')):
            for child in list(parent):
                remove=child.tag in ('PrecisionStateWriter','ConstantForceField')
                if name=='empty':remove=child.tag!='DefaultAnimationLoop' and not (child.tag=='RequiredPlugin' and 'AnimationLoop' in child.get('pluginName',''))
                if name=='mass_implicit' and child.tag=='BeamFEMForceField':remove=True
                if name=='beam_explicit':
                    if child.tag=='SparseLDLSolver':remove=True
                    if child.tag=='EulerImplicitSolver':child.tag='EulerExplicitSolver';child.attrib.clear()
                if remove:parent.remove(child)
        if name=='beam_explicit':node.insert(0,ET.Element('RequiredPlugin',name='forward',pluginName='Sofa.Component.ODESolver.Forward'))
        tree.write(scene_dir/'scene.scn',encoding='utf-8',xml_declaration=True)
        cmd=[str(ROOT/'build/next_headless/regrip_headless'),str(SOFA),str(scene_dir/'scene.scn'),'60000','0']
        row=measured(root/name,cmd);log=(root/name/'stdout.log').read_text()+(root/name/'stderr.log').read_text()
        row['completed']='60000 iterations done' in log and '[ERROR]' not in log;cases[name]=row
        write_json(root/'summary.json',cases);print(name,row['completed'],row['growth_kib'],flush=True)

if __name__=='__main__':main()
