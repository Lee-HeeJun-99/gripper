"""Locate actual unresolved plastic increments before changing any algorithm."""
import csv
import json
from curve_common import OUT,sha,write_json


def main():
    target=OUT/'phase_loss_localization_v1.json'
    if target.exists():raise ValueError('refuse overwritten actual bins')
    names=('full_coarse','full_fine','full_coarse_history1250nm');bounds=(.5,.6,.7,.8,.9,1.,1.25,1.5,2.,3.,4.,6.,7.,7.1,7.2,7.5,8.,10.,12.,14.,14.1,14.2,14.5,15.,15.1,15.2,15.5,16.,16.1,16.2,16.3,16.4,16.5,18.,24.);cases={}
    for name in names:
        path=OUT/name
        with(path/'contact.csv').open()as f:rows=list(csv.DictReader(f))
        points=[]
        for t in bounds:
            row=min(rows,key=lambda r:abs(float(r['time'])-t))
            if abs(float(row['time'])-t)>1e-8:raise ValueError('actual common epoch absent')
            points.append(dict(time=t,plastic=float(row['friction_dissipation']),detachment=float(row['release_dissipation']),contacts=int(float(row['contacts'])),slips=int(float(row['slip']))))
        intervals=[]
        for start,end in zip(points[:-1],points[1:]):
            inside=[r for r in rows if start['time']<float(r['time'])<=end['time']];previous=start['plastic'];changing=[]
            for r in inside:
                d=float(r['friction_dissipation'])
                if d!=previous:changing.append(float(r['time']))
                previous=d
            intervals.append(dict(start=start['time'],end=end['time'],plastic=end['plastic']-start['plastic'],detachment=end['detachment']-start['detachment'],recorded_plastic_change_frames=len(changing),last_plastic_change_time=max(changing)if changing else None,max_recorded_slips=max((int(float(r['slip']))for r in inside),default=None)))
        cases[name]=dict(source_sha256=sha(path/'contact.csv'),points=points,intervals=intervals)
    write_json(target,dict(status='EXPERIMENTAL',cases=cases,scope='actual sampled CSV increments;not every solver step or a reference solution. Distinguish decaying transient plasticity from a presumed quiet-roundoff floor before modifying object integration/friction. Existing relative FAILs are unchanged.'))
    for name,c in cases.items():print(name,[(r['start'],r['end'],r['plastic'],r['last_plastic_change_time'])for r in c['intervals']if r['plastic']and((.5<=r['start']<2)or(7<=r['start']<14)or(15<=r['start']<16))])


if __name__=='__main__':main()
