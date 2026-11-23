"""Actual load/state modal participation, not a repeated spectrum-only study.
Frozen rest chart, mapped mass, Native restK/rest CableJ; no contact or nonlinear
geometric/inertial terms. Reference algebra only; never writes SOFA states.
"""
import argparse,csv,json,sys,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigh,expm
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded

def inputs():
    src=BASE/'results/b3_first_free_step1159';root=ET.parse(src/'scene.scn').getroot();before=next(csv.DictReader((src/'step.phases.csv').open()));q=np.fromstring(before['body_q'],sep=' ').reshape(-1,3);frames=np.fromstring(before['guide_q'],sep=' ').reshape(-1,7);pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);ng=len(frames);nf=int(pairs[pairs[:,0]==0,1].max())+1;N=6*ng+3*nf;G=np.zeros((q.size,N))
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,6*ng+3*j:6*ng+3*j+3]=np.eye(3)
        else:
            b=j//3;r=q[i]-frames[b,:3];skew=np.array([[0,-r[2],r[1]],[r[2],0,-r[0]],[-r[1],r[0],0]]);G[3*i:3*i+3,6*b:6*b+3]=np.eye(3);G[3*i:3*i+3,6*b+3:6*b+6]=-skew
    K0=np.zeros((q.size,q.size))
    for r in csv.DictReader((src/'step.previous_K.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    mf=float(root.find("./Node[@name='finger0']/UniformMass").get('totalMass'))/len(q);M=mf*(G.T@G);fg=G.T@np.tile(mf*np.fromstring(root.get('gravity'),sep=' '),len(q));mp=BASE/'results/b3_rail_back_hold1129/guide_frames0.csv.mass.json'
    for i,m in enumerate(json.loads(mp.read_text())['elements']):M[6*i:6*i+6,6*i:6*i+6]+=m['matrix'];fg[6*i:6*i+3]+=m['mass_kg']*np.fromstring(root.get('gravity'),sep=' ')
    J=np.zeros((2,N))
    for r in csv.DictReader((src/'step.build_end.J.csv').open()):
        val=np.fromstring(r['values'],sep=' ');start=6*int(r['column']) if r['state']=='guide' else 6*ng+3*int(r['column']);J[int(r['row']),start:start+len(val)]=val
    free=np.ones(N,bool)
    for j in np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int):free[6*ng+3*j:6*ng+3*j+3]=False
    ix=np.ix_(free,free);return dict(M=M[ix],K=(G.T@K0@G)[ix],fg=fg[free],fc=J.sum(axis=0)[free],G=G[:,free],free=free,q=q,frames=frames,pairs=pairs,ng=ng,N=N,files=[src/'scene.scn',src/'step.phases.csv',src/'step.previous_K.csv',src/'step.build_end.J.csv',mp])

def state(case,d):
    folder=BASE/'results'/case;rows=list(csv.DictReader((folder/'finger0.csv').open()));gr=list(csv.DictReader((folder/'guide_frames0.csv').open()));assert len(rows)==len(gr);x=[];v=[];maperr=[];times=[]
    for r,g in zip(rows,gr):
        assert abs(float(r['time_s'])-float(g['time_s']))<1e-12
        body=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);vel=np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3);fr=np.fromstring(g['rigid_q'],sep=' ').reshape(-1,7);gv=np.fromstring(g['rigid_v'],sep=' ');xx=np.zeros(d['N']);vv=xx.copy();ng=d['ng'];rotation=(Rotation.from_quat(fr[:,3:])*Rotation.from_quat(d['frames'][:,3:]).inv()).as_rotvec();xx[:6*ng]=np.c_[fr[:,:3]-d['frames'][:,:3],rotation].ravel();vv[:6*ng]=gv
        for i,(owner,j) in enumerate(d['pairs']):
            if owner==0:xx[6*ng+3*j:6*ng+3*j+3]=body[i]-d['q'][i];vv[6*ng+3*j:6*ng+3*j+3]=vel[i]
        x.append(xx[d['free']]);v.append(vv[d['free']]);maperr.append(float(np.linalg.norm(d['G']@x[-1]-(body-d['q']).ravel())));times.append(float(r['time_s']))
    return rows,np.array(times),np.array(x),np.array(v),maperr

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
    if not a.worker:
        out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
    d=inputs();M=d['M'];K=d['K'];lam,V=eigh((K+K.T)/2,M);assert np.all(lam>0);fg=V.T@d['fg'];fc=V.T@d['fc'];n=len(lam);damp=1+1e-4*lam;trace=[];etas=[];files=d['files']+[Path(__file__)]
    # Unit C2 force polynomial, taken from actual NativeCableSequence closing=.5s.
    B=np.zeros((n,8,8));B[:,0,1]=1;B[:,1,0]=-lam;B[:,1,1]=-damp;B[:,1,5]=2.5*10/.5**3;B[:,1,6]=-2.5*15/.5**4;B[:,1,7]=2.5*6/.5**5
    for j in range(1,6):B[:,2+j,1+j]=j
    transitions=np.array([expm(.00125*b) for b in B]);z=np.zeros((n,8));z[:,2]=1;continuous=[]
    for step in range(1,249):z=np.einsum('nij,nj->ni',transitions,z);continuous.append(z[:,0].copy()*fc)
    s=np.sqrt((damp*damp/4-lam).astype(complex));r2=-damp/2-s;r1=-lam/(damp/2+s)
    references=[]
    for case,dt in [('b3_ode_force_candidate1176',.0025),('b3_ode_force_half1179',.00125)]:
        rows,t,x,v,maperr=state(case,d);eta=x@M@V;etav=v@M@V;etas.append(eta[::1 if dt==.0025 else 2] if dt==.0025 else eta[1::2]);eg=np.zeros(n);ec=np.zeros(n);vg=eg.copy();vc=ec.copy();errcon=[];be=[];native_error=[]
        for k,r in enumerate(rows):
            T=float(r['command_N']);expected=2.5*(10*(t[k]/.5)**3-15*(t[k]/.5)**4+6*(t[k]/.5)**5);assert abs(T-expected)<1e-12
            den=1+dt*damp+dt*dt*lam;vg=(vg+dt*(fg-lam*eg))/den;vc=(vc+dt*(fc*T-lam*ec))/den;eg+=dt*vg;ec+=dt*vc;contg=(fg/lam*(1+(r2*np.exp(r1*t[k])-r1*np.exp(r2*t[k]))/(r1-r2))).real;contc=continuous[round(t[k]/.00125)-1];errcon.append((eg+ec-contg-contc)**2);be.append(eg+ec);native_error.append((eta[k]-eg-ec)**2)
            if abs(t[k]/.0025-round(t[k]/.0025))<1e-10:trace.append(dict(case=case,time_s=t[k],native_modal_displacement_norm=float(np.linalg.norm(eta[k])),native_vs_frozen_BE_mass_norm=float(np.linalg.norm(eta[k]-eg-ec)),BE_vs_continuous_mass_norm=float(np.linalg.norm(eg+ec-contg-contc)),gravity_reference_mass_norm=float(np.linalg.norm(contg)),C2_reference_mass_norm=float(np.linalg.norm(contc)),rest_chart_body_error_L2_m=maperr[k]))
        references.append(dict(case=case,continuous_error_by_mode=np.sum(errcon,axis=0),native_reference_error_by_mode=np.sum(native_error,axis=0),initial_velocity_modal_norm=float(np.linalg.norm(etav[0])),max_chart_body_error_m=max(maperr)))
        files.extend([BASE/'results'/case/'finger0.csv',BASE/'results'/case/'guide_frames0.csv'])
    native_pair=np.sum((etas[0]-etas[1])**2,axis=0);rank=np.argsort(native_pair)[::-1];total=native_pair.sum();records=[]
    for i in range(n):records.append(dict(mode=i,frozen_Hz=float(np.sqrt(lam[i])/(2*np.pi)),gravity_projection=float(fg[i]),unit_Cable_projection=float(fc[i]),gravity_static_compliance_weight=float(fg[i]**2/lam[i]),Cable_static_compliance_weight=float(fc[i]**2/lam[i]),native_pair_squared_mass_error=float(native_pair[i]),native_pair_fraction=float(native_pair[i]/total),base_BE_continuous_squared_error=float(references[0]['continuous_error_by_mode'][i]),base_native_frozen_squared_error=float(references[0]['native_reference_error_by_mode'][i])))
    with (out/'modes.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    def top(load):
        weights=np.array([r[load] for r in records]);ids=np.argsort(weights)[-5:][::-1];return [dict(mode=int(i),Hz=records[i]['frozen_Hz'],fraction=float(weights[i]/weights.sum())) for i in ids]
    summary=dict(status='ACTUAL_LOAD_MODAL_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),top_native_time_error_modes=[records[i] for i in rank[:5]],top_gravity_compliance_modes=top('gravity_static_compliance_weight'),top_Cable_compliance_modes=top('Cable_static_compliance_weight'),reference_chart_limits=[{k:v for k,v in r.items() if not k.endswith('_by_mode')} for r in references],physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',scope='Actual commands and Native states projected on frozen restM/K/J. SO3 log chart,not full nonlinear trajectory reference;no contact,changingJ,geometric stiffness or convective inertia. Compliance weights are not measured energy.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'trace.json').write_text(json.dumps(trace,indent=2));print(json.dumps(summary))

if __name__=='__main__':main()
