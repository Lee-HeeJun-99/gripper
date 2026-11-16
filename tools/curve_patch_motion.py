"""Actual common-epoch prefix observables;do not invent a13.9s equilibrium."""
import csv
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import OUT,sha,write_json
from trial_validation import read_states
from closure_frame_evaluate import relative_angles
from curve_phase_assess import relative


def main():
    target=OUT/'patch_refinement_v2/prefix_motion_v1.json'
    if target.exists():raise ValueError('immutable prefix metrics exist')
    paths={'uniform1250':OUT/'full_coarse_history1250nm','local625':OUT/'patch_refinement_v2/local625_prefix82','local312':OUT/'patch_refinement_v2/local312_prefix82_record200'};cases={}
    for name,path in paths.items():
        root=ET.parse(path/'scene.scn').getroot();field=root.find('.//CurvedMaterialContact')
        if field is None:field=root.find('.//PatchRefinedContact')
        obj=int(field.get('objectIndex'));raw=[r for r in read_states(path/'state.txt')if r['time']<=8.2+1e-9];times=np.array([r['time']for r in raw]);x=np.array([r['X']for r in raw]).reshape(-1,obj+1,7);v=np.array([r['V']for r in raw]).reshape(-1,obj+1,6)
        start=int(np.argmin(abs(times-6)));end=int(np.argmin(abs(times-8.2)))
        if abs(times[start]-6)>1e-9 or abs(times[end]-8.2)>1e-9:raise ValueError('actual common endpoint missing')
        chosen=(times>=6-1e-9)&(times<=8.2+1e-9);q=x[chosen,obj,3:];angles=relative_angles(np.broadcast_to(x[start,obj,3:],q.shape),q)
        with(path/'contact.csv').open()as stream:row=min(csv.DictReader(stream),key=lambda r:abs(float(r['time'])-8.2))
        if abs(float(row['time'])-8.2)>1e-9:raise ValueError('actual contact epoch missing')
        cases[name]=dict(peak_translation_mm=float(np.linalg.norm(x[chosen,obj,:3]-x[start,obj,:3],axis=1).max()),peak_rotation_rad=float(angles.max()),end_object_speed=float(np.linalg.norm(v[end,obj,:3])),end_object_angular_speed=float(np.linalg.norm(v[end,obj,3:])),end_normal_force=float(row['normal_force']),end_capacity=float(row['capacity']),end_object_contact_force=[float(row[k])for k in('Fx','Fy','Fz')],end_object_contact_moment=[float(row[k])for k in('Mx','My','Mz')],end_coulomb_ratio=float(row['max_ratio']),raw_sha256={f:sha(path/f)for f in('state.txt','contact.csv')})
    comparisons={}
    for first,second in(('uniform1250','local625'),('local625','local312')):
        comparisons[first+'_'+second]={key:relative(cases[first][key],cases[second][key],.01)for key in('peak_translation_mm','peak_rotation_rad','end_normal_force','end_capacity')}
    write_json(target,dict(status='EXPERIMENTAL',cases=cases,comparisons=comparisons,scope='actual6--8.2s prefix peaks/common endpoint;NOT original13.9--14equilibrium metrics,full24recovery,mesh/dt/energy or12wrench approval. Force and moment vectors remain separate dimensional quantities.'))
    print({name:{k:(v['status'],v['relative'])for k,v in r.items()}for name,r in comparisons.items()})


if __name__=='__main__':main()
