"""Mesh-consistent planar interface metric via EB Hermite interior extrema.

This reconstructed research metric is distinct from directly sampled SOFA nodal
X slip. Never relabel sampled-node maxima as a continuous-interface maximum.
"""
import math

def interior_slip(position,layers,nodes,length,height):
    dx=length/(nodes-1);maximum=0.;where=None
    for l in range(layers-1):
        for i in range(nodes-1):
            coefficients=[];du=[]
            for j in (i,i+1):du.append(position[7*((l+1)*nodes+j)]-position[7*(l*nodes+j)])
            for layer in (l,l+1):
                a=layer*nodes+i;b=a+1;w0=position[7*a+2];w1=position[7*b+2]
                p0=-2*math.atan2(position[7*a+4],position[7*a+6]);p1=-2*math.atan2(position[7*b+4],position[7*b+6])
                coefficients.append((p0,6*(w1-w0)/dx-4*p0-2*p1,6*(w0-w1)/dx+3*p0+3*p1))
            a=du[0]+height/2*sum(c[0] for c in coefficients);b=du[1]-du[0]+height/2*sum(c[1] for c in coefficients);c=height/2*sum(v[2] for v in coefficients)
            points=[0.,1.]
            if c and 0<-b/(2*c)<1:points.append(-b/(2*c))
            for s in points:
                value=abs(a+b*s+c*s*s)
                if value>maximum:maximum=value;where=dict(interface=l,x=(i+s)*dx)
    return dict(max_reconstructed_slip_mm=maximum,location=where,scope='EB Hermite reconstruction from SOFA raw centroid/angle; not measured continuous film slip')
