"""Candidate quality/time sensitivity: no floors, no fabricated energy."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    def read(name):
        folder=BASE/'results'/name;rows=list(csv.DictReader((folder/'finger0.csv').open()));q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);v=np.array([np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3) for r in rows]);return folder,rows,q,v
    folder,rows,q,v=read('b3_rail_back_hold1129');half,hr,hq,hv=read('b3_rail_back_half1130');short,sr,sq,sv=read('b3_rail_back_force1128')
    mesh=json.loads((folder/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);t=np.array(mesh['tetrahedra']);rest=np.fromstring(ET.parse(folder/'scene.scn').getroot().find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
    index=np.array([int(np.argmin([abs(float(h['time_s'])-float(r['time_s'])) for h in hr])) for r in rows]);time_error=max(abs(float(hr[j]['time_s'])-float(r['time_s'])) for j,r in zip(index,rows));assert time_error<1e-12
    skin=local[:,2]==.1;rail=local[:,2]<0
    groups=[np.flatnonzero(skin&(abs(local[:,0]-x)<1e-12)) for x in np.unique(local[:,0])]
    def curvature(points):
        c=np.stack([points[...,g,:].mean(axis=-2) for g in groups],axis=-2);edge=np.diff(c,axis=-2);length=np.linalg.norm(edge,axis=-1);unit=edge/length[...,None]
        return 2*np.diff(unit,axis=-2)/(length[...,1:]+length[...,:-1])[...,None]
    fields={'skin_displacement':(q[:,skin]-rest[skin],hq[index][:,skin]-rest[skin]),'rail_displacement':(q[:,rail]-rest[rail],hq[index][:,rail]-rest[rail]),'velocity':(v,hv[index]),'skin_width_mean_curvature_change':(curvature(q)-curvature(rest),curvature(hq[index])-curvature(rest))}
    comparisons={}
    for key,(b,h) in fields.items():
        absolute=np.linalg.norm((b-h).reshape(len(rows),-1),axis=1);den=np.maximum(np.linalg.norm(b.reshape(len(rows),-1),axis=1),np.linalg.norm(h.reshape(len(rows),-1),axis=1));relative=np.divide(absolute,den,out=np.full_like(absolute,np.nan),where=den!=0);worst=int(np.nanargmax(relative));comparisons[key]=dict(maximum_absolute_L2_difference=float(absolute.max()),maximum_relative_error=float(relative[worst]),worst_time_s=float(rows[worst]['time_s']),undefined_zero_denominator_outputs=int((den==0).sum()),gate=.001,status='PASS_PAIR_OBSERVABLE_ONLY' if np.all(relative<=.001) else 'FAIL_PAIR_OBSERVABLE')
    quality={}
    for label,x in [('base',q),('half',hq)]:
        D0=(rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1);F=(x[:,t[:,1:]]-x[:,t[:,0,None]]).transpose(0,1,3,2)@np.linalg.inv(D0);s=np.linalg.svd(F,compute_uv=False);is_skin=np.all(local[t,2]>=0,axis=1)
        quality[label]=dict(maximum_absolute_Skin_principal_Green_strain=float(abs((s[:,is_skin]**2-1)/2).max()),minimum_volume_ratio=float(np.linalg.det(F).min()))
    d=dict(status='FAIL_TIME_PAIR_GATE' if any(x['status'].startswith('FAIL') for x in comparisons.values()) else 'PASS_PAIR_OBSERVABLES_ONLY',comparisons=comparisons,quality=quality,common_outputs=len(rows),max_common_time_error_s=time_error,short_to_long_prefix_q_error_m=float(abs(q[:len(sq)]-sq).max()),short_to_long_prefix_v_error_m_s=float(abs(v[:len(sv)]-sv).max()),material_allowable_strain=None,energy_work=None,full_time_convergence='NOT QUALIFIED:onepair only,noQuarter,noenergy',physical_validation='NOT QUALIFIED',holding='NOT RUN',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [folder/'finger0.csv',half/'finger0.csv',short/'finger0.csv',Path(__file__)]})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
