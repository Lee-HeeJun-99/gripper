"""Check actual saved clocks before attributing time error only to friction."""
import csv
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import OUT,FRAME,ROOT,sha,write_json


def main():
    target=OUT/'controller_clock_audit_v1.json'
    if target.exists():raise ValueError('refuse overwritten clock evidence')
    frozen=FRAME.parent/'Integrated.inc';text=frozen.read_text()
    if 't>=times[i]-1e-12'not in text:raise ValueError('compiled controller schedule differs from audited definition')
    results={}
    for name in('base','halfdt','quarterdt','repeat24'):
        path=OUT/'grasp'/name;r=json.loads((path/'metrics.json').read_text());c=r['config'];h=c['dt'];steps=round(c['duration']/h)
        times=np.empty(steps+1);times[0]=0
        for i in range(1,steps+1):times[i]=times[i-1]+h
        with(path/'state.txt').open()as f:actual=[float(s[2:])for s in f if s.startswith('T=')]
        simulated=times[::20]
        if len(actual)!=len(simulated)or not np.array_equal(np.array(actual),simulated):raise ValueError('reconstructed clock does not bit-match ALL actual saved times: '+name)
        tree=ET.parse(path/'scene.scn');body=tree.getroot().find('Node');events=[];seen=set()
        for tag,tkey,vkey in(('RoutedCable','commandTimes','commandValues'),('FrameLayerNetwork','pressureTimes','pressureValues'),('SpatialLoad','times','values')):
            for e in body.findall(tag):
                t=list(map(float,e.get(tkey,'').split()));v=list(map(float,e.get(vkey,'').split()));key=(tag,tuple(t),tuple(v))
                if key in seen:continue
                seen.add(key)
                for time,value in zip(t,v):
                    ideal=round(time/h)
                    if abs(ideal*h-time)>32*np.finfo(float).eps*max(1.,abs(time)):raise ValueError('audit only claims exact-grid events')
                    i=int(np.searchsorted(times,time-1e-12))
                    if i>steps:continue
                    events.append(dict(component=tag,requested_time=time,value=value,ideal_begin_step=ideal,actual_begin_step=i,extra_steps=i-ideal,actual_clock_time=float(times[i]),error_seconds=float(times[i]-time)))
        with(path/'layer0.csv').open()as f:layer=list(csv.DictReader(f))
        e=body.find('FrameLayerNetwork');schedule=list(zip(map(float,e.get('pressureTimes').split()),map(float,e.get('pressureValues').split())))
        pressure_errors=[]
        for row in layer:
            t=float(row['time']);expected=0
            for event,value in schedule:
                if t>=event-1e-12:expected=value
            pressure_errors.append(abs(expected-float(row['pressure'])))
        results[name]=dict(status='FAIL'if any(e['extra_steps']for e in events)else'PASS',actual_saved_clock_bitmatch=True,actual_frames=len(actual),events=events,actual_pressure_csv_max_difference=max(pressure_errors),scope='force evaluations use BEGIN clock;history Commit uses END clock. Event-grid shift is reconstructed only after every saved clock bit-matches;pressure CSV independently validates schedule semantics.')
    write_json(target,dict(status='FAIL'if any(r['status']=='FAIL'for r in results.values())else'PASS',cases=results,compiled_schedule_source_sha256=sha(frozen),SDK_time_source=str(ROOT/'.runtime/sofa-source/Sofa/framework/Simulation/Core/src/sofa/simulation/DefaultAnimationLoop.cpp'),reason='DefaultAnimationLoop repeatedly adds binary dt;1e-12 schedule margin can be smaller than accumulated clock roundoff;this does not alone establish the cause of dissipation error'))
    print({n:[(e['component'],e['requested_time'],e['extra_steps'])for e in r['events']if e['extra_steps']]for n,r in results.items()})


if __name__=='__main__':main()
