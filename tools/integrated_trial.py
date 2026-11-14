"""Bounded multilayer SOFA, material-guide cable and contact research experiments.

No settings from the certified legacy scene are changed. All dimensions/loads are
explicit uncalibrated research parameters; sampled raw state and provenance saved.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from dataclasses import dataclass,asdict
from integrated_common import ROOT,SOFA,BUILD,OUT,sha,write_json,provenance
from integrated_build import sources
from native_scene import PLUGINS
from run_trial import execute_process
from trial_validation import read_states

@dataclass
class Config:
    layers:int=2
    nodes:int=11
    length:float=100.
    height:float=.4
    k:float=1.
    mode:int=0
    normal_k:float=0.
    load:float=1e-6
    moment:float=0.
    dt:float=.0005
    duration:float=12.
    stride:int=20
    connectors:tuple=()
    pressure:float=0.
    mu:float=.3
    width:float=8.
    pressure_times:tuple=()
    pressure_values:tuple=()
    load_times:tuple=()
    load_values:tuple=()
    cable_tension:float=0.
    cable_k:float=0.
    shortening:float=0.
    cable_offset:float=-.2
    cable_times:tuple=()
    cable_values:tuple=()
    cable_all_layers:bool=True
    object_shape:int=-1
    object_x:float=100.
    object_z:float=-5.
    object_radius:float=5.
    object_fixed:bool=True
    contact_k:float=.001
    object_load:float=0.
    equal_total_material:bool=False
    kind:str='equilibrium'

    def validate(self):
        data=asdict(self)
        for key,field in self.__dataclass_fields__.items():
            value=data[key]
            if field.type is float and (type(value) not in (int,float) or not math.isfinite(value)):raise ValueError('invalid numeric '+key)
            if field.type is bool and type(value) is not bool:raise ValueError('invalid boolean '+key)
        if type(self.mode) is not int or type(self.object_shape) is not int:raise ValueError('invalid integer mode/shape')
        if type(self.layers) is not int or self.layers not in (2,4,8) or type(self.nodes) is not int or not 3<=self.nodes<=41:raise ValueError('layer/node resource bound')
        if type(self.stride) is not int or self.stride<1 or self.mode not in (0,1,2) or self.object_shape not in (-1,0,1,2) or self.kind not in ('equilibrium','transient'):raise ValueError('invalid mode/kind/stride')
        for key,value in asdict(self).items():
            if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite '+key)
        if min(self.length,self.height,self.dt,self.duration,self.width,self.object_radius)<=0 or max(self.k,self.normal_k,self.pressure,self.mu,self.cable_tension,self.cable_k,self.shortening,self.contact_k)<0:raise ValueError('invalid physical parameter')
        if min(self.k,self.normal_k,self.pressure,self.mu,self.cable_tension,self.cable_k,self.shortening,self.contact_k)<0:raise ValueError('negative parameter')
        steps=round(self.duration/self.dt)
        if steps<1 or steps>120000 or self.duration>60 or abs(steps*self.dt-self.duration)>1e-10 or steps%self.stride:raise ValueError('bounded integral sample steps required')
        if self.connectors and (len(set(self.connectors))!=len(self.connectors) or any(type(i) is not int or not 1<=i<self.nodes for i in self.connectors)):raise ValueError('connector selection')
        if self.mode==1 and self.k<=0:raise ValueError('slider requires positive elastic stiffness')
        if self.mode==2 and self.normal_k>0:raise ValueError('finite rotation cannot use planar confinement')
        for times,values in [(self.load_times,self.load_values),(self.pressure_times,self.pressure_values),(self.cable_times,self.cable_values)]:
            if len(times)!=len(values) or any(not math.isfinite(v) for v in (*times,*values)) or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('invalid schedule')
        return steps

def sequence(values):return ' '.join(map(str,values))

def force_reference(c):
    value=max(abs(c.load),abs(c.moment)/c.length,c.cable_tension*abs(c.cable_offset)/c.length,c.cable_k*c.shortening*abs(c.cable_offset)/c.length,*(map(abs,c.load_values) or [0]))
    return value if value else 1e-6 # absolute check only for genuinely zero applied load

def interface_slips(x,c,height):
    def rotate(q,v):
        def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
        a=cross(q[:3],v);b=cross(q[:3],a)
        return [v[j]+2*(q[3]*a[j]+b[j]) for j in range(3)]
    slips=[]
    for layer in range(c.layers-1):
        for i in range(1,c.nodes):
            l=7*(layer*c.nodes+i);u=l+7*c.nodes;ql=x[l+3:l+7];qu=x[u+3:u+7]
            if c.mode==2:
                t=rotate(ql,(1,0,0));a=rotate(ql,(0,0,height/2));b=rotate(qu,(0,0,-height/2))
                slips.append(sum(t[j]*(x[u+j]-x[l+j]+b[j]-a[j]) for j in range(3)))
            else:slips.append(x[u]-x[l]-height*(math.atan2(ql[1],ql[3])+math.atan2(qu[1],qu[3])))
    return slips

def geometry(c):
    I=8*.4**3/12;r=(4*I/math.pi)**.25;h=c.height
    if c.equal_total_material:r*=math.sqrt(2/c.layers);I=math.pi*r**4/4;h*=math.sqrt(2/c.layers)
    return r,math.pi*r*r,I,h

def scene(out,c):
    r,A,I,h=geometry(c);n=c.nodes;L=c.layers
    root=ET.Element('Node',name='ReGrip_Integrated_RESEARCH',dt=str(c.dt),gravity='0 0 0')
    for i,p in enumerate(PLUGINS):ET.SubElement(root,'RequiredPlugin',name='p'+str(i),pluginName='Sofa.Component.'+p)
    ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='.2',rayleighStiffness='.1')
    ET.SubElement(root,'EigenSparseLU',name='solver')
    body=ET.SubElement(root,'Node',name='Multilayer')
    poses=[[c.length*i/(n-1),0,(l-(L-1)/2)*h,0,0,0,1] for l in range(L) for i in range(n)]
    if c.object_shape>=0:poses.append([c.object_x,0,c.object_z,0,0,0,1])
    ET.SubElement(body,'MechanicalObject',name='dofs',template='Rigid3d',position=sequence(v for p in poses for v in p))
    ET.SubElement(body,'MeshTopology',name='edges',lines=sequence(v for l in range(L) for i in range(n-1) for v in (l*n+i,l*n+i+1)))
    mass=2e-5 if c.equal_total_material else 1e-5*L
    ET.SubElement(body,'UniformMass',totalMass=str(mass))
    ET.SubElement(body,'BeamFEMForceField',radius=str(r),radiusInner='0',youngModulus='250',poissonRatio='.32')
    fixed=[l*n for l in range(L)]+([L*n] if c.object_shape>=0 and c.object_fixed else [])
    ET.SubElement(body,'FixedProjectiveConstraint',indices=sequence(fixed))
    tips=[(l+1)*n-1 for l in range(L)]
    if c.load_times:ET.SubElement(body,'ScheduledLoad',name='scheduled_load',indices=sequence(tips),times=sequence(c.load_times),values=sequence(c.load_values))
    else:ET.SubElement(body,'ConstantForceField',indices=sequence(tips),forces=sequence(v for _ in range(L) for v in (0,0,-c.load/L,0,c.moment/L,0)))
    attributes=dict(name='network',nodesPerLayer=str(n),layers=str(L),mode=str(c.mode),stiffness=str(c.k),height=str(h),normalStiffness=str(c.normal_k),pressure=str(c.pressure),mu=str(c.mu),width=str(c.width),length=str(c.length))
    if c.connectors:attributes['connectorIndices']=sequence(c.connectors)
    if c.pressure_times:attributes.update(pressureTimes=sequence(c.pressure_times),pressureValues=sequence(c.pressure_values))
    ET.SubElement(body,'LayerNetwork',**attributes)
    if c.cable_tension or c.cable_k or c.cable_times:
        for l in (range(L) if c.cable_all_layers else (0,)):
            a=dict(name='cable'+str(l),route=sequence(range(l*n,(l+1)*n)),offsetZ=str(c.cable_offset),stiffness=str(c.cable_k),shortening=str(c.shortening),tension=str(c.cable_tension/L if c.cable_all_layers else c.cable_tension))
            if c.cable_times:a.update(commandTimes=sequence(c.cable_times),commandValues=sequence(c.cable_values))
            ET.SubElement(body,'RoutedCable',**a)
    if c.object_shape>=0:
        ET.SubElement(body,'AnalyticContact',name='object_contact',objectIndex=str(L*n),shape=str(c.object_shape),pointIndices=sequence(range(1,L*n)),radius=str(c.object_radius),halfX=str(c.object_radius),halfY=str(c.object_radius),halfZ=str(c.object_radius),stiffness=str(c.contact_k),pointRadius='.1')
        if c.object_load:ET.SubElement(body,'ConstantForceField',name='object_external',indices=str(L*n),forces=f'0 0 {-c.object_load} 0 0 0')
    ET.SubElement(body,'IntegratedRecorder',filename=str(out/'state.txt'),stride=str(c.stride))
    ET.indent(root);ET.ElementTree(root).write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    return dict(radius=r,area=A,inertia=I,height=h,total_mass=mass,fixed=fixed,total_beam_nodes=L*n)

def analyze(out,c,g,process,log,rest_reference=None):
    steps=c.validate();raw=read_states(out/'state.txt');nodes=c.layers*c.nodes+(c.object_shape>=0)
    if process['exit_code']!=0 or process['process_status']!='exited' or '[ERROR]' in log or f'{steps} iterations done' not in log:raise ValueError('SOFA exit/error/completion failure')
    if len(raw)!=steps//c.stride+1:raise ValueError('incomplete sampled raw states')
    initial=raw[0]['X'] if rest_reference is None else rest_reference;rows=[];maxrot=0;maxslip=0
    F=force_reference(c)
    free=[i for i in range(nodes) if i not in g['fixed']]
    for step,r in enumerate(raw):
        x,v,R=r.get('X',[]),r.get('V',[]),r.get('R',[])
        if len(x)!=7*nodes or len(v)!=6*nodes or len(R)!=6*nodes or not all(math.isfinite(a) for a in x+v+R+[r['time']]):raise ValueError('invalid/nonfinite state')
        if abs(r['time']-step*c.dt*c.stride)>1e-9:raise ValueError('time mismatch')
        if any(abs(x[7*i+j]-initial[7*i+j])>1e-10 for i in g['fixed'] for j in range(7)):raise ValueError('clamped node moved')
        for i in range(nodes):
            q=x[7*i+3:7*i+7];angle=2*math.atan2(math.sqrt(sum(a*a for a in q[:3])),abs(q[3]));maxrot=max(maxrot,angle)
            if abs(sum(a*a for a in q)-1)>1e-8:raise ValueError('quaternion norm')
            if i<g['total_beam_nodes'] and c.mode!=2 and (angle>=.005 or max(abs(q[0]),abs(q[2]))>1e-8):raise ValueError('small planar domain exceeded')
        tips=[-(x[7*((l+1)*c.nodes-1)+2]-initial[7*((l+1)*c.nodes-1)+2]) for l in range(c.layers)]
        slips=interface_slips(x,c,g['height'])
        maxslip=max(maxslip,max(map(abs,slips),default=0))
        rf=max(abs(R[6*i+j]) for i in free for j in range(3));rt=max(abs(R[6*i+j]) for i in free for j in range(3,6))
        rows.append(dict(time=r['time'],tip=sum(tips)/c.layers,layer_tips=tips,slip=max(map(abs,slips),default=0),
            velocity=max(abs(v[6*i+j]) for i in free for j in range(3)),angular_velocity=max(abs(v[6*i+j]) for i in free for j in range(3,6)),
            residual=max(rf/(F/c.layers),rt/(F*c.length/c.layers)),reaction_z=-sum(R[6*i+2] for i in g['fixed']),
            reaction_y=-sum(R[6*i+4]+x[7*i+2]*R[6*i]-x[7*i]*R[6*i+2] for i in g['fixed']),
            object_displacement=math.sqrt(sum((x[7*(nodes-1)+j]-initial[7*(nodes-1)+j])**2 for j in range(3))) if c.object_shape>=0 else 0))
    tail=rows[-max(2,round(.1/(c.dt*c.stride))):];last=rows[-1]
    drift=(max(r['tip'] for r in tail)-min(r['tip'] for r in tail))/max(abs(last['tip']),1e-10)
    equilibrium=max(r['velocity'] for r in tail)<1e-5 and max(r['angular_velocity'] for r in tail)<1e-5 and max(r['residual'] for r in tail)<1e-3 and drift<1e-4
    with (out/'metrics_series.csv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=[k for k in last if k!='layer_tips']);writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in rows)
    return dict(status=('PASS' if equilibrium else 'not_converged') if c.kind=='equilibrium' else 'EXPERIMENTAL',
        execution_completed=True,equilibrium_validated=equilibrium,tip_deflection_mm=last['tip'],layer_tip_mm=last['layer_tips'],
        max_interface_slip_mm=last['slip'],peak_interface_slip_mm=maxslip,max_rotation_rad=maxrot,relative_residual=last['residual'],
        final_velocity=last['velocity'],drift=drift,object_displacement_mm=last['object_displacement'],reaction_z=last['reaction_z'],reaction_y=last['reaction_y'],
        effective_stiffness=c.load/last['tip'] if equilibrium and last['tip']>0 and c.load>0 and not c.load_times and not c.cable_tension and not c.cable_k and not c.moment and c.object_shape<0 else None,samples=len(rows))

def run(out,c):
    c.validate();manifest=json.loads((BUILD/'plugin/manifest.json').read_text());plugin=BUILD/'plugin/libReGripIntegrated.so'
    if manifest['sources']!=sources() or manifest['binary_sha256']!=sha(plugin):raise RuntimeError('integrated source/binary manifest mismatch')
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);g=scene(out,c)
    cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(c.duration/c.dt)),'--hideProgressBar','-l',str(plugin),str(out/'scene.scn')]
    report=dict(provenance=provenance(),config=asdict(c),geometry=g,status='incomplete',scope='EXPERIMENTAL model_F_mm_s; not PET or real vacuum/grasp verification',binary_sha256=sha(plugin),model_sources=manifest['sources'],runner_sha256=sha(__file__),execution_completed=False,equilibrium_validated=False,effective_stiffness=None)
    write_json(out/'config.json',asdict(c));write_json(out/'command.json',cmd);write_json(out/'metrics.json',report)
    process=execute_process(cmd,out,180);report.update(process);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    try:report.update(analyze(out,c,g,process,log))
    except (OSError,ValueError,KeyError,OverflowError) as e:report.update(status='FAIL',failure_reason=str(e))
    report['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'}
    write_json(out/'metrics.json',report);print(out.name,report['status'],report.get('tip_deflection_mm'),report.get('relative_residual'),flush=True);return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('config',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    c=Config(**json.loads(a.config.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x))))
    r=run(a.out,c);raise SystemExit(0 if r['status'] in ('PASS','EXPERIMENTAL') else 1)
