"""Independent static two-layer Euler-Bernoulli + axial FEM.
Coordinates x along beam; bending w along z. Interface shear slip only.
No SOFA Python force injection is used. Units match v105: mm, force units.
"""
import csv
from pathlib import Path
import numpy as np

L=30.0; B=8.0; H=.4; E=250.0; N=11; F_TOTAL=1e-4
HERE=Path(__file__).resolve().parent
# 2 layers, each node (u,w,theta); normal separation not penalized

def solve(k_per_connector, n=N):
    dof=6*n; dx=L/(n-1)
    M=np.zeros((dof,dof),dtype=float)
    R=np.zeros((dof,),dtype=float)
    EI=E*B*H**3/12.; EA=E*B*H
    def idx(layer,node,component): return 3*(layer*n+node)+component
    for layer in range(2):
        for el in range(n-1):
            i,j=el,el+1
            a=EA/dx
            for m,p in enumerate((i,j)):
                for q,nod in enumerate((i,j)):
                    M[idx(layer,p,0),idx(layer,nod,0)]+=a*(1 if m==q else -1)
            C=(EI/dx**3)*np.array([[12,6*dx,-12,6*dx],
                   [6*dx,4*dx**2,-6*dx,2*dx**2],
                   [-12,-6*dx,12,-6*dx],
                   [6*dx,2*dx**2,-6*dx,4*dx**2]])
            ids=[idx(layer,i,1),idx(layer,i,2),idx(layer,j,1),idx(layer,j,2)]
            M[np.ix_(ids,ids)]+=C
        R[idx(layer,n-1,1)]=-F_TOTAL/2
    # b * DOFs = relative upper-bottom interface tangential displacement.
    # u_upper + h/2 theta_upper - (u_lower - h/2 theta_lower)
    connectors=[]
    for node in range(1,n):
        b=np.zeros(dof)
        b[idx(1,node,0)]=1; b[idx(0,node,0)]=-1
        b[idx(1,node,2)]=H/2; b[idx(0,node,2)]=H/2
        M+=k_per_connector*np.outer(b,b)
        connectors.append(b)
    fixed=[idx(layer,0,comp) for layer in range(2) for comp in range(3)]
    free=np.array([i for i in range(dof) if i not in fixed])
    v=np.zeros(dof)
    v[free]=np.linalg.solve(M[np.ix_(free,free)],R[free])
    delta=-.5*(v[idx(0,n-1,1)]+v[idx(1,n-1,1)])
    slips=np.array([b@v for b in connectors]); shears=k_per_connector*slips
    elastic_bend_axial=.5*sum(v[i]*R[i] for i in range(dof))-.5*k_per_connector*np.dot(slips,slips)
    return {'k_connector':k_per_connector,'n_nodes':n,'deflection_mm':delta,
            'effective_stiffness':F_TOTAL/delta,'max_abs_x_slip_mm':max(abs(slips)),
            'rms_x_slip_mm':np.sqrt(np.mean(slips**2)),
            'max_abs_connector_force':max(abs(shears)),
            'shear_spring_energy':.5*k_per_connector*np.dot(slips,slips),
            'bend_axial_energy':elastic_bend_axial,
            'external_work':F_TOTAL*delta,'residual_inf':np.max(abs(M[np.ix_(free,free)]@v[free]-R[free])),
            'slips':slips,'node_xs':np.linspace(dx,L,n-1)}

def main():
    ks=[0,1e-6,1e-5,1e-4,.001,.01,.1,1,10,1e2,1e4,1e6]
    cases=[solve(k) for k in ks]
    k0=cases[0]['effective_stiffness']
    names=['k_connector','n_nodes','deflection_mm','effective_stiffness','relative_to_free',
           'max_abs_x_slip_mm','rms_x_slip_mm','max_abs_connector_force',
           'shear_spring_energy','bend_axial_energy','external_work','residual_inf']
    with (HERE/'comparison_V106_static.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        writer=csv.DictWriter(fp,fieldnames=names);writer.writeheader()
        for c in cases:
            writer.writerow({key:c['effective_stiffness']/k0 if key=='relative_to_free' else c[key] for key in names})
    with (HERE/'slips_V106_static.csv').open('w',newline='',encoding='utf-8-sig') as fp:
        writer=csv.writer(fp);writer.writerow(['k_connector','x_mm','interface_slip_x_mm'])
        for c in cases:
            for x,s in zip(c['node_xs'],c['slips']):writer.writerow([c['k_connector'],x,s])
    print('K | tip deflection(mm) | ratio to FREE | max slip(mm) | residual')
    for c in cases:
        print(f"{c['k_connector']:>8g} | {c['deflection_mm']:.9g} | {c['effective_stiffness']/k0:.7g} | {c['max_abs_x_slip_mm']:.7g} | {c['residual_inf']:.2e}")
    free=cases[0]['effective_stiffness']; stiff=cases[-1]['effective_stiffness']
    assert abs(free-2*(E*B*H**3/12.)*3/L**3)/(2*(E*B*H**3/12.)*3/L**3)<1e-6
    assert abs(stiff/free-4)<.05, f'large-k limit ratio {stiff/free} is not near 4 (finite node discretization)'
    assert all(x['residual_inf'] < 1e-8 for x in cases)
    print('PASS: free limit and bonded limit checked; SOFA tangential coupling NOT YET validated.')

if __name__=='__main__':main()
