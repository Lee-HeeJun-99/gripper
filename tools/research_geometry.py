"""Independent centerline interpolation audit; NEVER a counterfactual SOFA run."""
import math,json,xml.etree.ElementTree as ET
import numpy as np
from scipy.integrate import quad
from research_common import OUT,write_json
def analytic():
    length=100.;tip=.1;cx=47.3;radius=5.;penetration=.005
    def w(x):return tip*x*x*(3*length-x)/(2*length**3)
    def slope(x):return tip*3*x*(2*length-x)/(2*length**3)
    cy=radius+w(cx)-penetration
    def force(fn):return quad(lambda x:max(0.,radius-math.hypot(x-cx,fn(x)-cy)),cx-1,cx+1,epsabs=1e-13,epsrel=1e-11,limit=300)
    reference,reference_error=force(w);rows=[]
    for nodes in(11,21,41):
        X=np.linspace(0,length,nodes);Y=w(X);D=slope(X)
        def hermite(x):
            i=min(int(x/length*(nodes-1)),nodes-2);L=X[i+1]-X[i];s=(x-X[i])/L
            return(2*s**3-3*s*s+1)*Y[i]+(s**3-2*s*s+s)*L*D[i]+(-2*s**3+3*s*s)*Y[i+1]+(s**3-s*s)*L*D[i+1]
        linear=force(lambda x:float(np.interp(x,X,Y)))[0];high=force(hermite)[0]
        rows.append(dict(nodes=nodes,linear_normal_integral=linear,linear_relative_error=abs(linear-reference)/reference,hermite_normal_integral=high,hermite_relative_error=abs(high-reference)/reference))
    return dict(origin='independent prescribed cubic cantilever geometry,not solved FEM/SOFA',assumptions=dict(length_mm=length,tip_mm=tip,sphere_radius_mm=radius,center_x_mm=cx,penetration_mm=penetration,kn=1),reference=reference,reference_estimated_absolute_error=reference_error,reference_integration='SciPy adaptive quadrature epsabs1e-13/epsrel1e-11',rows=rows)
def saved_x(path,target=13.99):
    initial=None;selected=None;best=float('inf');t=0
    with path.open()as f:
        for line in f:
            if line.startswith('T='):t=float(line[2:])
            elif line.startswith('X='):
                if initial is None:initial=np.fromstring(line[2:],sep=' ').reshape(-1,7)
                if abs(t-target)<best:best=abs(t-target);selected=np.fromstring(line[2:],sep=' ').reshape(-1,7)
                if t>target+.02:break
    return initial,selected
def actual(name):
    path=OUT/'grasp'/name
    if not(path/'metrics.json').exists():return dict(status='NOT RUN')
    c=json.loads((path/'config.json').read_text());field=ET.parse(path/'scene.scn').getroot().find('.//MaterialPointContact');skin=float(field.get('pointRadius'));radius=float(field.get('radius'))
    if field.get('shape')!='0':raise ValueError('offline audit is sphere only')
    n=c['nodes'];initial,x=saved_x(path/'state.txt');s=(np.arange(4096)+.5)/4096;h00=2*s**3-3*s*s+1;h10=s**3-2*s*s+s;h01=-2*s**3+3*s*s;h11=s**3-s*s
    def director(q):
        a,b,c,d=q;return np.array([1-2*(b*b+c*c),2*(a*b+d*c),2*(a*c-d*b)])
    results={};maximum=0
    for mode in('linear','director_hermite'):
        total=0
        for layer in range(6):
            for i in range(n-1):
                a=layer*n+i;b=a+1;L=np.linalg.norm(initial[b,:3]-initial[a,:3]);line=(1-s[:,None])*x[a,:3]+s[:,None]*x[b,:3];curve=h00[:,None]*x[a,:3]+h01[:,None]*x[b,:3]+L*h10[:,None]*director(x[a,3:])+L*h11[:,None]*director(x[b,3:]);maximum=max(maximum,float(np.linalg.norm(curve-line,axis=1).max()));p=line if mode=='linear'else curve;depth=skin-(np.linalg.norm(p-x[-1,:3],axis=1)-radius)
                total+=c['normal_k']*L*float(np.maximum(depth,0).mean())
        results[mode]=total
    return dict(status='EXPERIMENTAL',origin='OFFLINE geometry reconstruction of actual SOFA state,not a re-solved equilibrium',normal_integrals=results,relative_mapping_difference=abs(results['linear']-results['director_hermite'])/abs(results['director_hermite']),maximum_centerline_difference_mm=maximum,quadrature='4096 fixed reference midpoint samples per edge; no friction/history or new force/Jacobian',warning='Hermite virtual-work/rotation mapping and curved-contact detection must be validated before actual implementation; nodal-data error remains')
def main():
    result=dict(analytic=analytic(),actual={n:actual(n)for n in('h_quarter','fine_n21','fine_n41')});write_json(OUT/'geometry_diagnostic.json',result);print(result)
if __name__=='__main__':main()
