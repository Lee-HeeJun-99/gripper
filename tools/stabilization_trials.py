"""Same physical problems, isolated audit plugin, numerical solver experiments."""
import argparse
import json
import xml.etree.ElementTree as ET
from dataclasses import asdict,replace
from integrated_trial import Config,scene,analyze,force_reference
from stabilization_common import ROOT,SOFA,OUT,BUILD,PLUGIN,write_json,sha,provenance
from run_trial import execute_process

def run(name,c,static=False,linear='EigenSparseLU',steps=None,initial=None,newton_fraction=5e-4):
    if not 0<newton_fraction<=1e-3:raise ValueError('Newton stopping may not exceed physical force criterion')
    c.validate();out=OUT/name;out.mkdir(parents=True,exist_ok=False);g=scene(out,c);tree=ET.parse(out/'scene.scn');root=tree.getroot()
    ode=root.find('EulerImplicitSolver');ode.set('computeResidual','true')
    if static:
        ode.tag='StaticSolver';ode.attrib.clear();ode.set('newtonSolver','@newton')
        ET.SubElement(root,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton='40',relativeSuccessiveStoppingThreshold='0',relativeInitialStoppingThreshold='0',absoluteResidualStoppingThreshold=str(force_reference(c)/c.layers*newton_fraction),relativeEstimateDifferenceThreshold='0',absoluteEstimateDifferenceThreshold='0',maxNbIterationsLineSearch='10',lineSearchCoefficient='.5',warnWhenLineSearchFails='true')
    solver=root.find('EigenSparseLU');solver.tag=linear
    if linear=='SparseLDLSolver':solver.set('template','CompressedRowSparseMatrixd')
    if linear=='CGLinearSolver':solver.set('iterations','2000');solver.set('tolerance','1e-16');solver.set('threshold','1e-30')
    if linear=='CGLinearSolver':root.insert(0,ET.Element('RequiredPlugin',name='iterative_plugin',pluginName='Sofa.Component.LinearSolver.Iterative'))
    if linear=='SparseLUSolver':root.insert(0,ET.Element('RequiredPlugin',name='csparse_plugin',pluginName='CSparseSolvers'))
    body=root.find('Node');ET.SubElement(body,'ForceAudit',filename=str(out/'forces.txt'),after=str(max(0,c.duration-.1)),stride=str(c.stride))
    if initial:
        from trial_validation import read_states
        obj=body.find('MechanicalObject');obj.set('rest_position',obj.get('position'));obj.set('position',' '.join(map(str,read_states(initial)[-1]['X'])))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    settings=dict(**asdict(c),static_solver=static,linear_solver=linear,newton_fraction=newton_fraction,initial=str(initial) if initial else 'cold')
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(steps or round(c.duration/c.dt)),'--hideProgressBar','-l',str(PLUGIN),str(out/'scene.scn')]
    write_json(out/'config.json',settings);write_json(out/'command.json',command)
    r=dict(config=settings,provenance=provenance(),binary_sha256=sha(PLUGIN));p=execute_process(command,out,180);r['process']=p
    try:r.update(analyze(out,c,g,p,(out/'stdout.log').read_text()+(out/'stderr.log').read_text()))
    except (ValueError,OSError,KeyError) as e:r.update(status='FAIL',reason=str(e))
    r['artifacts']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.name!='metrics.json'};write_json(out/'metrics.json',r)
    print(name,r['status'],r.get('relative_residual'),flush=True);return r

def main():
    p=argparse.ArgumentParser();p.add_argument('suite',choices=['probe','newton','static','regression','eight']);a=p.parse_args();rows={}
    if a.suite=='probe':
        cases=[('small',Config(k=0,load=0,normal_k=.001,cable_tension=1e-6,duration=.01,stride=1)),('L8',Config(layers=8,k=100,duration=.01,stride=1))]
        for name,c in cases:rows[name]=run('probe/'+name,c)
    elif a.suite=='newton':
        for name,c in [('small',Config(k=0,load=0,normal_k=.001,cable_tension=1e-6)),('length',Config(k=0,load=0,normal_k=.001,cable_k=.01,shortening=.0001)),('wire_pressure',Config(mode=1,k=1,pressure=1e-8,normal_k=.001,load=0,cable_tension=1e-5)),('L8',Config(layers=8,k=100))]:
            rows[name]=run('newton/'+name,replace(c,dt=.001,duration=.02,stride=1),static=True)
    elif a.suite=='static':
        d=Config(layers=8,k=100,duration=.15)
        cases=[('L8_free',replace(d,k=0)),('L8_k1',replace(d,k=1)),('L8_k10',replace(d,k=10)),('L8_base',d),('L8_halfdt',replace(d,dt=.00025)),('L8_quarterdt',replace(d,dt=.000125)),('L8_mesh',replace(d,nodes=21,connectors=tuple(range(2,21,2)))),('L8_repeat',d),
               ('small',Config(k=0,load=0,normal_k=.001,cable_tension=1e-6,duration=.15)),('length',Config(k=0,load=0,normal_k=.001,cable_k=.01,shortening=.0001,duration=.15)),('wire_pressure',Config(mode=1,k=1,pressure=1e-8,normal_k=.001,load=0,cable_tension=1e-5,duration=.15))]
        for name,c in cases:
            rows[name]=run('static/'+name,c,static=True);write_json(OUT/'static/summary.json',rows)
    elif a.suite=='regression':
        for L in (2,4):rows[str(L)]=run('regression/L'+str(L),Config(layers=L,k=100))
    else:
        for name,c in [('free',Config(layers=8,k=0)),('k1',Config(layers=8,k=1)),('k10',Config(layers=8,k=10)),('k100',Config(layers=8,k=100)),('halfdt',Config(layers=8,k=100,dt=.00025)),('quarterdt',Config(layers=8,k=100,dt=.000125)),('mesh',Config(layers=8,k=100,nodes=21,connectors=tuple(range(2,21,2)))),('extended',Config(layers=8,k=100,duration=18))]:
            rows[name]=run('eight/'+name,c);write_json(OUT/'eight/summary.json',rows)
    write_json(OUT/a.suite/'summary.json',rows)

if __name__=='__main__':main()
