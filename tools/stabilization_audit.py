"""Independent per-component sums, boundary separation and absolute DOF residuals."""
import json
import numpy as np
from stabilization_common import OUT,write_json
from trial_validation import read_states
from integrated_trial import Config,force_reference

def audit(directory):
    data=json.loads((directory/'config.json').read_text());c=Config(**{k:v for k,v in data.items() if k in Config.__dataclass_fields__})
    snapshots={};time=None
    for line in (directory/'forces.txt').read_text().splitlines():
        if line.startswith('T '):time=float(line[2:]);snapshots[time]={}
        elif line.startswith('F '):
            _,kind,name,values=line.split(' ',3);snapshots[time][kind+':'+name]=np.fromstring(values,sep=' ').reshape(-1,6)
    raw=read_states(directory/'state.txt');last=raw[-1];states=np.array(last['X']).reshape(-1,7);R=np.array(last['R']).reshape(-1,6)
    fields=snapshots[min(snapshots,key=lambda t:abs(t-last['time']))];total=sum(fields.values());n=c.layers*c.nodes
    fixed=[l*c.nodes for l in range(c.layers)];free=[i for i in range(n) if i not in fixed]
    f=total[free,:3];m=total[free,3:];worst=np.unravel_index(abs(f).argmax(),f.shape);node=free[worst[0]];axis=int(worst[1]);scale=force_reference(c)/c.layers
    components={}
    for name,v in fields.items():
        components[name]=dict(max_free_force=float(abs(v[free,:3]).max()),max_free_torque=float(abs(v[free,3:]).max()),worst_total_dof_contribution=float(v[node,axis]),net_force=v[:,:3].sum(axis=0).tolist(),net_moment=(v[:,3:]+np.cross(states[:,:3],v[:,:3])).sum(axis=0).tolist())
    return dict(sum_vs_original_recorder_max_abs=float(abs(total-R).max()),force_denominator=scale,moment_denominator=scale*c.length,
        absolute_force_residual=float(abs(f).max()),absolute_moment_residual=float(abs(m).max()),relative_force=float(abs(f).max()/scale),relative_moment=float(abs(m).max()/(scale*c.length)),
        worst_force_node=node,worst_force_axis=axis,components=components,boundary_reaction=(-total[fixed]).sum(axis=0).tolist(),
        free_net_force=total[free,:3].sum(axis=0).tolist(),free_net_moment=(total[free,3:]+np.cross(states[free,:3],total[free,:3])).sum(axis=0).tolist(),
        note='gravity zero; no contact/constraint cable in these scenes. Fixed roots excluded. Constraint reaction is inferred from root balance, not mixed into free residual.')

def main():
    results={}
    for phase in ('newton','static','regression'):
        for p in sorted((OUT/phase).glob('*/forces.txt')):
            try:results[str(p.parent.relative_to(OUT))]=audit(p.parent)
            except (ValueError,KeyError) as e:results[str(p.parent.relative_to(OUT))]=dict(status='FAIL',reason=str(e))
    write_json(OUT/'force_audit.json',results);print({k:v.get('sum_vs_original_recorder_max_abs') for k,v in results.items()})

if __name__=='__main__':main()
