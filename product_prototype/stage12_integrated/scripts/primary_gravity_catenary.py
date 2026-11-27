"""Independent P1 inextensible massive-string contrast on actual drum/terminal ports.
No bending stiffness/friction/elastic cable/source allowables or hardware certificate.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from primary_gravity_pullback import G,C,RADIUS,FREE0,rot,drot
from primary_gravity_swivel import FreeSwivel,ARM
class Catenary:
 def __init__(self,points,order=16):
  self.points=points;self.gravity=FreeSwivel(points);self.order=order;z,w=leggauss(order);self.u=(z+1)/2;self.weights=w/2;self.wire=next(p for p in points if p['mode']=='wire');self.mu=self.wire['mass_kg']/(FREE0+.006)
 def cable(self,P,beta,eta,phi,T,factor=1.):
  r=RADIUS;e=np.array([np.sin(beta),np.cos(beta)]);E=P+ARM*e;Q=C+r*np.array([np.cos(phi),np.sin(phi)]);tq=np.array([-np.sin(phi),np.cos(phi)]);start=np.pi/2-eta;arc=r*(start-phi);length=FREE0-arc;tail=C+rot(eta)@[-.003,r];torque_g_rotor=sum(p['mass_kg']*G*factor*(rot(eta)@(np.array(p['rest_centroid_m'])[[0,2]]-C))[0] for p in self.points if p['mode']=='rotor');torque_g_wrap=self.mu*G*factor*r*r*(np.sin(start)-np.sin(phi));torque_g_tail=self.mu*.006*G*factor*(tail-C)[0];S=T-(torque_g_rotor+torque_g_wrap+torque_g_tail)/r
  h0=-S*tq;w=self.mu*G*factor
  def integral(s):
   ss=np.asarray(s);h=np.stack((np.broadcast_to(h0[0],ss.shape+(self.order,)),h0[1]+w*ss[...,None]*self.u),axis=-1);unit=h/np.sqrt(np.sum(h*h,axis=-1))[...,None];return ss[...,None]*np.einsum('...ij,i->...j',unit,self.weights)
  end=Q+integral(length);Fe=S*tq-np.array([0,w*length]);ss=length*self.u;positions=Q+integral(ss);moment_free=length*np.einsum('ij,i->j',positions,self.weights);moment_wrap=r*r*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc;moment_tail=.006*tail;wc=(moment_free+moment_wrap+moment_tail)/(FREE0+.006)
  return dict(E=E,Q=Q,end=end,Fe=Fe,S=S,length=length,arc_length=arc,eta=eta,phi=phi,start=start,wire_centroid=wc,wire_total_length=length+arc+.006,free_positions=positions,free_material_stations=ss,shape_integral=integral,wire_weight=w*length,torque_g_rotor=torque_g_rotor,torque_g_wrap=torque_g_wrap,torque_g_tail=torque_g_tail)
 def body(self,v,n,beta,factor=1.,details=False):
  # Only finger-attached masses contribute rod/swivel equations. Rotor and wire
  # have their own actual string/drum equilibrium; never count them twice.
  selected=[p for p in self.points if p['mode'] not in ('wire','rotor')];return FreeSwivel(selected).evaluate(np.r_[v,beta],n,factor,details)
 def mass_positions(self,v,n,beta,eta,cable,factor=1.):
  _,_,pp,_=self.body(v,n,beta,factor,True)
  for item in self.points:
   if item['mode'] not in ('wire','rotor'):continue
   q=cable['wire_centroid'] if item['mode']=='wire' else C+rot(eta)@(np.array(item['rest_centroid_m'])[[0,2]]-C);pp.append(dict(part_ID=item['part_ID'],mode=item['mode'],mass_kg=item['mass_kg'],position_m=[float(q[0]),item['rest_centroid_m'][1],float(q[1])]))
  return pp
