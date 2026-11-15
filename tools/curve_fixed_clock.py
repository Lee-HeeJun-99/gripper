"""Independent exact-index clock contrast,SDK mechanics and schedule unchanged."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from curve_common import ROOT,OUT,PREFIX,identity,sha,write_json
from curve_compensation import run as prepare
from history_trial import analyze
from closure_validation_suite import logged
from birth_monitor import Monitor
from run_trial import execute_process
BUILD=ROOT/'build/autonomous_20261116_fixed_clock_a01/v1'
PLUGIN=BUILD/'libReGripFixedStepClock.so'
SOURCES=[ROOT/'models/fixed_step_clock'/n for n in('Clock.h','FixedStepClock.cpp','CMakeLists.txt')]+[ROOT/'tests/test_fixed_clock.cpp']


def build():
    out=OUT/'build_clock_v1';out.mkdir(parents=True,exist_ok=False)
    for p in SOURCES:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    hashes={str(p.relative_to(ROOT)):sha(p)for p in SOURCES};write_json(out/'sources.json',hashes)
    if(BUILD/'build_manifest.json').exists():
        old=json.loads((BUILD/'build_manifest.json').read_text())
        if old['sources']!=hashes or old['binary']!=sha(PLUGIN):raise ValueError('immutable fixed-clock build changed;new build version required')
        write_json(out/'summary.json',dict(status='PASS',reused_immutable_build=True,**old));return
    if PLUGIN.exists():raise ValueError('unmanifested existing binary;do not overwrite it')
    for stage,command in[('unit_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',SOURCES[-1],'-o',out/'unit.bin']),('unit',[out/'unit.bin']),('configure',['cmake','-S','models/fixed_step_clock','-B',BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',BUILD,'-j2']),('ldd',['ldd',PLUGIN])]:
        r=logged(command,out/stage,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=stage,process=r));return
    manifest=dict(sources=hashes,binary=sha(PLUGIN),runtime=identity(),scope='integer-index fixed-step time only;SDK DefaultAnimationLoop still executes all mechanics;no changed schedule tolerance')
    write_json(BUILD/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('fixed-clock math/build PASS')


def run(name,dt=.0005,profile=False,wall=480,duration=18,nodes=21,history=.0025):
    manifest=json.loads((BUILD/'build_manifest.json').read_text())
    if sha(PLUGIN)!=manifest['binary']or any(sha(ROOT/p)!=h for p,h in manifest['sources'].items()):raise ValueError('compiled clock source/binary changed')
    out=prepare(name,dt=dt,profile=profile,duration=duration,nodes=nodes,history=history,prepare_only=True)
    tree=ET.parse(out/'scene.scn');root=tree.getroot();loop=root.find('DefaultAnimationLoop')
    if loop is None:raise ValueError('expected one original SDK loop')
    loop.tag='FixedStepClockAnimationLoop';loop.set('filename',str(out/'clock.csv'))
    root.insert(0,ET.Element('RequiredPlugin',name='FixedIndexClock',pluginName=str(PLUGIN)));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    config=json.loads((out/'config.json').read_text());config['clock_model']='fixed_step_integer_index;unchanged SDK mechanics and control margin'
    write_json(out/'config.json',config);ident=json.loads((out/'identity.json').read_text());ident['fixed_clock']=manifest;write_json(out/'identity.json',ident)
    command=json.loads((out/'command.json').read_text());monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process)
    if profile:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();steps=round(4/dt);result=dict(status='EXPERIMENTAL'if not process['exit_code']and'[ERROR]'not in log and f'{steps} iterations done'in log else'FAIL',config=config,identity=ident,process=process,scope='actual4s fixed-clock profile,not hold qualification')
    else:result=analyze(out,config,process)
    result['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()};write_json(out/'metrics.json',result);print(name,result['status'],process['runtime_s'],result.get('global_moment_residual'),flush=True);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--dt',type=float,default=.0005);p.add_argument('--profile',action='store_true');p.add_argument('--wall',type=int,default=480);p.add_argument('--duration',type=float,default=18);a=p.parse_args()
    if a.name=='build':build()
    else:run(a.name,dt=a.dt,profile=a.profile,wall=a.wall,duration=a.duration)
