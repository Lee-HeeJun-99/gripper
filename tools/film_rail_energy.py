"""Independent discrete energy audit of a synchronized frictionless assembly.
Signed, analytically derived integration defects are not fitted dissipation.
"""
import argparse,csv,json,struct,subprocess,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='20261116_rail_recovery90');a=p.parse_args()
    for name in (a.tag,a.case):
        if not name.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);base=ROOT/'results'/('autonomous_film_'+a.case)
    summary=json.loads((base/'summary.json').read_text());identity=json.loads((base/'identity.json').read_text())
    if summary['status']!='PASS' or 'order="1" theta=".5"' not in (base/'1/scene.scn').read_text():raise RuntimeError('requires complete actual trapezoid assembly')
    rows=list(csv.DictReader((base/'1/journal.csv').open()));x=np.array([np.fromstring(r['x'],sep=' ').reshape(-1,3) for r in rows]);n=x.shape[1];nx=n//11;rest=[]
    for offset,ny,width,thickness,y,z in identity['layout']:
        for i in range(nx):
            for j in range(ny):rest.append([100*i/(nx-1),y+width*j/(ny-1),z])
    u=x-np.array(rest);time=np.r_[0.,[float(r['time']) for r in rows]];u=np.concatenate([np.zeros_like(u[:1]),u]);v=np.zeros_like(u)
    for i in range(1,len(u)):v[i]=2*(u[i]-u[i-1])/(time[i]-time[i-1])-v[i-1]
    speed=np.max(np.linalg.norm(v[1:],axis=2),axis=1);recorded=np.array([float(r['max_speed']) for r in rows]);speed_error=float(max(abs(speed-recorded)))
    if speed_error>1e-7:raise RuntimeError('kinematic reconstruction failed '+str(speed_error))
    tension=np.r_[0.,[float(r['T_per_rail']) for r in rows]];binary=out/'states.bin'
    with binary.open('xb') as stream:
        stream.write(struct.pack('QQ',n,len(time)))
        for i,t in enumerate(time):stream.write(struct.pack('dd',t,tension[i]));stream.write(np.concatenate([u[i],v[i]],axis=1).astype(np.float64).tobytes())
    source=ROOT/'diagnostics/film_rail_tendon/EnergyAudit.cpp';shutil.copy2(source,out/source.name)
    build=logged(['g++','-std=c++17','-O2','-ffp-contract=off',source,'-o',out/'audit'],out/'compile',180)
    if build['exit_code']:raise RuntimeError('energy compiler')
    process=logged([out/'audit',binary],out/'audit_process',480)
    if process['exit_code']:raise RuntimeError('energy kernel')
    audit=list(csv.DictReader((out/'audit_process/stdout.log').open()))
    if len(audit)!=len(rows):raise RuntimeError('energy time rows')
    arrays={k:np.array([float(r[k]) for r in audit]) for k in audit[0]}
    totals={k:float(sum(arrays[k])) for k in ('delta_energy','tendon_path_work','tendon_force_work','elastic_quadrature_defect','damping_trapezoid','damping_discrete','damping_quadrature_defect','identity_residual')}
    work_scale=float(max(abs(np.cumsum(arrays['tendon_path_work']))));closure=float(max(abs(np.cumsum(arrays['identity_residual']))))
    Urecord=np.array([float(r['U_shell'])+float(r['U_attachment']) for r in rows]);Krecord=np.array([float(r['K']) for r in rows]);energy_error=float(max(abs(Urecord-arrays['U'])));kinetic_error=float(max(abs(Krecord-arrays['K'])))
    result=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),tool_sha256=sha(__file__),binary_sha256=sha(out/'audit'),input_journal_sha256=sha(base/'1/journal.csv'),totals=totals,
        maximum_cumulative_identity_residual=closure,relative_to_peak_work=closure/work_scale if work_scale else None,maximum_reconstructed_speed_error=speed_error,
        maximum_stored_energy_reconstruction_error=energy_error,maximum_kinetic_energy_reconstruction_error=kinetic_error,
        status='PASS' if work_scale and closure/work_scale<=.001 else 'FAIL',
        definitions=dict(identity='Delta(K+U)=W_path-D_trap+(W_force-W_path)-Q_elastic+(D_trap-D_discrete)+unexplained_residual',damping='gamma=2: D_trap=h*m*(v_n²+v_prev²),D_discrete=2*m*du²/h;difference=.5*h*m*dv²',
                         elastic='Q_elastic=.5*(gradU_n+gradU_prev).du-DeltaU',tendon='W_force=.5*(f_t_n+f_t_prev).du;W_path=-.5*(T_n+T_prev)*DeltaLength;generator is not cable elastic storage'),
        scope='actual accepted SOFA q/T/K journals plus independent frictionless assembly force reconstruction;not in-engine transaction instrumentation or full ReGrip energy approval',
        missing_from_full_grasp=['pressure/vacuum work','layer friction','object contact/friction','free-object energy','wire guide friction','self-collision'])
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
