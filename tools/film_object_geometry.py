"""Explicit closed faceted cylinder; no analytical-cylinder equivalence claim."""
import math
def cylinder_y(center=(75.,12.,-8.2),radius=8.,height=40.,segments=64):
 if segments<8 or radius<=0 or height<=0:raise ValueError('cylinder dimensions')
 points=[(center[0]+radius*math.cos(2*math.pi*i/segments),center[1]+side*height/2,center[2]+radius*math.sin(2*math.pi*i/segments)) for side in (-1,1) for i in range(segments)]
 points.extend([(center[0],center[1]-height/2,center[2]),(center[0],center[1]+height/2,center[2])]);faces=[]
 for i in range(segments):
  j=(i+1)%segments;faces.extend([(i,segments+i,j),(segments+i,segments+j,j),(2*segments,i,j),(2*segments+1,segments+j,segments+i)])
 return points,faces
