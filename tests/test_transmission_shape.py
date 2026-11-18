"""Discrete3D curvature/centre-vs-width metrics;not a contact coverage test."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import numpy as np
from film_transmission_linear import shape
u=np.zeros((231,3));assert shape(u.ravel())['skin_max_total_curvature_per_mm']==0
s=np.linspace(0,100,21);R=100.
for start,ny in ((0,5),(105,3),(168,3)):
 p=u[start:start+21*ny].reshape(21,ny,3);p[:,:,0]=(R*np.sin(s/R)-s)[:,None];p[:,:,2]=(R*(1-np.cos(s/R)))[:,None]
metrics=shape(u.ravel());expected=.05/(2*R*np.sin(.05/2))
for part in ('skin','left','right'):
 assert abs(metrics[part+'_max_total_curvature_per_mm']-expected)<1e-12
 assert abs(metrics[part+'_root_tip_total_angle_rad']-.95)<1e-12
print('PASS independent analytic discrete circle/straight line,total3D curvature and root-tip angle;NOT wrapping/contact')
