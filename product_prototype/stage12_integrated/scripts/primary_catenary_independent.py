"""Independent closed-form string integral and adaptive centroid quadrature."""
import numpy as np
from scipy.integrate import quad
from primary_gravity_independent import positions,R,G
RAD=.01125;C=np.array([0.,.020])
def inspect_string(row,points):
 eta=row['rotor_angle_rad'];phi=row['drum_tangent_phi_rad'];start=np.pi/2-eta;Q=C+RAD*np.array([np.cos(phi),np.sin(phi)]);tq=np.array([-np.sin(phi),np.cos(phi)]);S=row['wire_start_tension_N'];length=row['wire_free_length_m'];total=row['wire_length_m'];mu=next(p['mass_kg'] for p in points if p['mode']=='wire')/total;w=mu*G*row['gravity_factor'];h=-S*tq
 def displacement(s):
  if w==0:return s*h/S
  hx,hz=h;v=hz+w*s;return np.array([hx/w*(np.arcsinh(v/hx)-np.arcsinh(hz/hx)),(np.hypot(hx,v)-S)/w])
 end=Q+displacement(length);mom_free=np.array([quad(lambda s:(Q+displacement(s))[i],0,length,epsabs=1e-12,epsrel=1e-12)[0] for i in range(2)]);arc=RAD*(start-phi);mom_wrap=RAD**2*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc;tail=C+R(eta)@[-.003,RAD];wc=(mom_free+mom_wrap+.006*tail)/total;E=np.array(row['cable_end_m']);Fe=-h-np.array([0,w*length]);rotg=sum(p['mass_kg']*G*row['gravity_factor']*(R(eta)@(np.array(p['rest_centroid_m'])[[0,2]]-C))[0] for p in points if p['mode']=='rotor');wrapg=mu*G*row['gravity_factor']*RAD**2*(np.sin(start)-np.sin(phi));tailg=mu*.006*G*row['gravity_factor']*(tail-C)[0];torque=RAD*(S-row['T_N'])+rotg+wrapg+tailg
 # Force and tangent differential equation from closed form, independent centered differences.
 s=.413*length;eps=1e-5*length;tangent_num=(displacement(s+eps)-displacement(s-eps))/(2*eps);hs=h+[0,w*s];tangent_error=np.max(abs(tangent_num-hs/np.linalg.norm(hs)));end_error=np.max(abs(end-E));centroid_error=np.max(abs(wc-row['wire_centroid_m']));fe_error=np.max(abs(Fe-row['cable_exit_force_XZ_N']));length_error=abs(arc+length+.006-total)
 return dict(n=row['n'],endpoint_error_m=float(end_error),centroid_error_m=float(centroid_error),endpoint_force_error_N=float(fe_error),drum_torque_balance_error_Nm=float(abs(torque)),length_error_m=float(length_error),closed_form_tangent_error=float(tangent_error),passed=bool(end_error<1e-10 and centroid_error<1e-10 and fe_error<1e-12 and abs(torque)<1e-12 and length_error<1e-12 and tangent_error<1e-5))
