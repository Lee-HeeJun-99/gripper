"""Finite swept-wire/axisymmetric eyelet geometry; no Native dynamics claim."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def solid_distance(points, polygon):
    """Signed Euclidean distance to a closed meridional solid polygon."""
    p=np.asarray(points); poly=np.asarray(polygon); distance=np.full(len(p),np.inf);inside=np.zeros(len(p),bool)
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        edge=b-a;t=np.clip((p-a)@edge/(edge@edge),0,1)
        distance=np.minimum(distance,np.linalg.norm(p-a-t[:,None]*edge,axis=1))
        if b[1]!=a[1]:
            cross=(a[1]>p[:,1])!=(b[1]>p[:,1])
            inside^=cross & (p[:,0] < a[0]+(p[:,1]-a[1])*(b[0]-a[0])/(b[1]-a[1]))
    return np.where(inside,-distance,distance)

def fillet(point,u,v,radius=5.):
    angle=np.arccos(np.clip(u@v,-1,1));trim=radius*np.tan(angle/2)
    if angle<1e-9:return np.array([point]),0.,0.
    normal=(v-u*np.cos(angle))/np.sin(angle);start=point-trim*u
    count=max(2,int(np.ceil(radius*angle/.005)))
    s=np.linspace(0,angle,count+1)
    arc=start+radius*np.sin(s)[:,None]*u+radius*(1-np.cos(s))[:,None]*normal
    return arc,float(trim),float(radius*angle/count)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True);args=parser.parse_args()
    out=BASE/'results'/args.tag;out.mkdir(exist_ok=False)
    source=BASE/'results/four_route_gate1408/summary.json';d=json.loads(source.read_text());records=[];arcs=[]
    # Explicit 0.2mm x45deg chamfers, unchanged central ID1.2/OD3/length2.
    poly=[[.8,-1],[1.5,-1],[1.5,1],[.8,1],[.6,.8],[.6,-.8]]
    for route_id,route in enumerate(d['routes']):
        q=np.array(route['route_mm']);trims=[]
        for k in range(1,len(q)-1):
            point=q[k];u=point-q[k-1];u/=np.linalg.norm(u);v=q[k+1]-point;v/=np.linalg.norm(v)
            axis=u+v;axis/=np.linalg.norm(axis);arc,trim,spacing=fillet(point,u,v)
            # Include incoming/outgoing portions through and beyond both faces.
            before=np.linspace(point-(trim+2)*u,arc[0],401);after=np.linspace(arc[-1],point+(trim+2)*v,401)
            samples=np.vstack([before,arc,after]);delta=samples-point;z=delta@axis;radial=np.linalg.norm(delta-z[:,None]*axis,axis=1)
            maxstep=max(spacing,(trim+2-trim)/400)
            margin=float(solid_distance(np.column_stack([radial,z]),poly).min()-.25-maxstep/2)
            records.append(dict(route=route_id,guide=k-1,turn_deg=float(np.degrees(np.arccos(u@v))),trim_mm=trim,swept_wire_solid_clearance_lower_bound_mm=margin))
            arcs.append(dict(route=route_id,guide=k-1,points_mm=arc.tolist(),arc_spacing_mm=spacing));trims.append(trim)
        for k in range(len(trims)-1):
            records.append(dict(route=route_id,between_guides=[k,k+1],remaining_straight_span_mm=float(np.linalg.norm(q[k+2]-q[k+1])-trims[k]-trims[k+1])))
    minimum=min(x['swept_wire_solid_clearance_lower_bound_mm'] for x in records if 'trim_mm'in x)
    span=min(x['remaining_straight_span_mm'] for x in records if 'between_guides'in x)
    result=dict(status='PASS_LOCAL_CHAMFER_FILLET_GEOMETRY_ONLY' if min(minimum,span)>0 else 'REJECT_CHAMFER_FILLET_GEOMETRY',minimum_clearance_lower_bound_mm=minimum,minimum_remaining_span_mm=span,wire_radius_mm=.25,bend_radius_mm=5,eyelet_meridional_solid_polygon_mm=poly,records=records,arcs=arcs,terminal_anchor='NOT QUALIFIED: no through-bore at terminated cable end',manufacturing_tolerance=None,wire_contact_friction=None,Native='NOT RUN',scope='Initial geometric candidate, not equilibrium of a flexible wire, manufacturing or four-route assembly qualification. Lipschitz sample bound subtracts half maximum arclength interval and finite wire radius; original straight-bore FAIL retained.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_sha256=sha(source))
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(result['status'],minimum,span)
if __name__=='__main__':main()
