"""Same-binary actual surface-event refinement; preserves failed relative gates."""
import argparse,csv,json,math,os,shutil,subprocess
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json

def read(path):
    return list(csv.DictReader(path.open()))

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    cases=[];sources={}
    for name in a.cases:
        d=ROOT/'results'/('autonomous_film_'+name);identity=json.loads((d/'identity.json').read_text());summary=json.loads((d/'summary.json').read_text())
        if summary['status']!='PASS':raise ValueError('incomplete/failed input '+name)
        if identity.get('accepted_replay'):raise ValueError('replay is not a complete time-refinement trajectory;FF work inventory resets')
        states=read(d/'event.csv.states.csv');film=read(d/'film.csv');events=read(d/'event.csv.surface.csv')
        if not identity.get('owner_ode'):raise ValueError('assessment requires ODE-stage committed states')
        cases.append((name,identity,states,film,events))
        for file in ('identity.json','summary.json','event.csv.states.csv','event.csv.surface.csv','film.csv','scene.scn'):
            sources[str((d/file).relative_to(ROOT))]=sha(d/file)
    if any(c[1]['binary_sha256']!=cases[0][1]['binary_sha256'] or c[1]['mode']!=cases[0][1]['mode'] or c[1]['duration']!=cases[0][1]['duration'] for c in cases):raise ValueError('binary/physical input mismatch')
    metrics={};passed=True
    def error(x,y):
        x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
        absolute=float(np.max(np.abs(x-y)));scale=float(np.max(np.abs(y)))
        relative=absolute/scale if scale else (0 if absolute==0 else None)
        return dict(absolute=absolute,reference_scale=scale,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
    for i in range(len(cases)):
        for j in range(i+1,len(cases)):
            left,right=cases[i],cases[j];ls={round(float(r['time']),12):r for r in left[2]};rs={round(float(r['time']),12):r for r in right[2]};times=sorted(set(ls)&set(rs))
            if not times:raise ValueError('no common physical sample times')
            result={}
            for key in ('local_displacement','local_velocity'):
                result[key]=error([list(map(float,ls[t][key].split())) for t in times],[list(map(float,rs[t][key].split())) for t in times])
            lf={round(float(r['time']),12):r for r in left[3]};rf={round(float(r['time']),12):r for r in right[3]}
            for key in ('U_shell','U_attachment','K','tendon_work','cable_length'):
                result[key]=error([float(lf[t][key]) for t in times],[float(rf[t][key]) for t in times])
            def atoms(rows):
                groups={}
                for r in rows:groups.setdefault(r['event_id'],[]).append(r)
                return [[float(v[0]['event_time']),sum(float(r['impulse']) for r in v),float(v[0]['impact_loss'])] for v in groups.values()]
            la,ra=atoms(left[4]),atoms(right[4])
            if len(la)!=len(ra):result['event_count']=dict(status='FAIL',left=len(la),right=len(ra))
            elif la:
                for k,key in enumerate(('event_time','total_impact_impulse','impact_loss')):result[key]=error([r[k] for r in la],[r[k] for r in ra])
            phases={}
            if la and ra:
                entryLow=min(la[0][0],ra[0][0]);entryHigh=max(la[0][0],ra[0][0])
                for phase,selected in (('pre_contact',[t for t in times if t<entryLow]),('entry',[t for t in times if entryLow<=t<=entryHigh]),('post_contact',[t for t in times if t>entryHigh])):
                    if not selected:phases[phase]=dict(status='NOT SAMPLED',sample_count=0);continue
                    phase_errors={key:error([float(lf[t][key]) for t in selected],[float(rf[t][key]) for t in selected]) for key in ('U_shell','U_attachment','K','tendon_work')}
                    phases[phase]=dict(sample_count=len(selected),first_time=selected[0],last_time=selected[-1],metrics=phase_errors)
                    passed &= all(v['status']=='PASS' for v in phase_errors.values())
            pair=left[0]+'__'+right[0];metrics[pair]=dict(common_times=times,metrics=result,phases=phases)
            passed &= all(v['status']=='PASS' for v in result.values())
    os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    for name,identity,states,film,events in cases:
        time=[float(r['time']) for r in film]
        for ax,key in zip(axes.flat,('skin_tip_z','U_attachment','K','T_per_rail')):
            base=identity['duration']/identity['steps'];label=name[-3:]+' dt='+str(base)
            if identity.get('local_divisor',1)!=1:label+=' -> '+str(base/identity['local_divisor'])
            ax.plot(time,[float(r[key]) for r in film],label=label);ax.set_title(key);ax.set_xlabel('time [s]');ax.grid()
    axes.flat[0].legend();fig.suptitle('Actual SOFA fixed-sphere coupon; NOT qualified grasp');fig.tight_layout();fig.savefig(out/'actual_time.png',dpi=160);plt.close(fig)
    write_json(out/'summary.json',dict(status='PASS' if passed else 'FAIL',scope='same-binary limited coupon .1% relative time gate;NOT full-cycle/energy/grasp',grid_note='explicit local nonuniform grids;NOT uniform base-to-quarter convergence' if any(c[1].get('local_divisor',1)!=1 for c in cases) else 'uniform-step comparisons',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,metrics=metrics))
    print(json.dumps(dict(status='PASS' if passed else 'FAIL',path=str(out))))
if __name__=='__main__':main()
