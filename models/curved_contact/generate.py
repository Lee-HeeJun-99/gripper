"""Independent director-Hermite component; frozen inherited models untouched."""
import sys
from pathlib import Path
source=Path(sys.argv[1]).read_text().replace('MaterialPointContact','CurvedMaterialContact').replace('ReGripMaterialPointContact','ReGripCurvedContact')
def section(begin,end,value):
    global source
    a=source.index(begin);b=source.index(end,a);source=source[:a]+value+source[b:]
section(' Pose point(', ' // Boundary values',r'''
 Pose point(const VecCoord&x,unsigned edge,double s)const{Pose p;unsigned a=segments.getValue()[2*edge],b=segments.getValue()[2*edge+1];p.p=regrip_curved::position(pose(x[a]),pose(x[b]),s,grids[edge].length);return p;}
 double sag(const VecCoord&x,unsigned e)const{return regrip_curved::sagBound(pose(x[segments.getValue()[2*e]]),pose(x[segments.getValue()[2*e+1]]),grids[e].length);}
''')
section(' void checkTemporal(', ' sofa::core::objectmodel::Data<std::string>journalFilename',r'''
 void checkTemporal(const VecCoord&x)const{
  auto obj=pose(x[objectIndex.getValue()]),oldObj=pose(previous[objectIndex.getValue()]);
  auto local=[&](const V&p,const Pose&o){return rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p,o.p));};
  for(unsigned e=0;e<grids.size();++e){auto a0=beforeLocal(e,0),b0=beforeLocal(e,1),a1=local(point(x,e,0).p,obj),b1=local(point(x,e,1).p,obj);double motion=std::max(std::sqrt(dot(sub(a1,a0),sub(a1,a0))),std::sqrt(dot(sub(b1,b0),sub(b1,b0))));
   for(unsigned endpoint=0;endpoint<2;++endpoint){unsigned id=segments.getValue()[2*e+endpoint];auto d0=rotate(Q{-oldObj.q[0],-oldObj.q[1],-oldObj.q[2],oldObj.q[3]},rotate(pose(previous[id]).q,V{1,0,0})),d1=rotate(Q{-obj.q[0],-obj.q[1],-obj.q[2],obj.q[3]},rotate(pose(x[id]).q,V{1,0,0}));auto delta=sub(d1,d0);motion+=grids[e].length*(4./27)*std::sqrt(dot(delta,delta));}
   if(motion==0)continue;
   auto range=regrip_closure::activeInterval(a0,b0,shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue()+sag(previous,e)+motion);auto selected=bounds(range,grids[e].count);
   for(int i=selected.first;i<=selected.last;++i){double s=(i+.5)/grids[e].count;auto p=beforeLocal(e,s),q=local(point(x,e,s).p,obj);if(regrip_closure::sdf(p,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue()&&regrip_closure::sdf(q,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue())regrip_birthlaw::transientDepth(p,q,shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue());}
  }
 }
''')
section(' regrip_closure::Interval interval(', ' Assembly assemble(',r'''
 regrip_closure::Interval interval(const VecCoord&x,unsigned edge)const{auto o=pose(x[objectIndex.getValue()]);auto a=point(x,edge,0),b=point(x,edge,1);return regrip_closure::activeInterval(regrip_closure::localPoint(a,b,o,0),regrip_closure::localPoint(a,b,o,1),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue()+sag(x,edge));}
 // Both normal and tangent are fixed reference-material midpoint integrals.
 // interval() is a conservative candidate envelope,NOT the true contact patch.
 Snapshot evaluate(const VecCoord&x,bool derivatives)const{
  validateInput(x);checkTemporal(x);Snapshot out(x.size());unsigned obj=objectIndex.getValue();auto object=pose(x[obj]);
  for(unsigned edge=0;edge<grids.size();++edge){auto selected=bounds(interval(x,edge),grids[edge].count);unsigned a=segments.getValue()[2*edge],b=segments.getValue()[2*edge+1];auto pa=pose(x[a]),pb=pose(x[b]);double L=grids[edge].length,weight=L/grids[edge].count;double block[18][18]{},forces[18]{};unsigned ids[18];for(int j=0;j<6;++j){ids[j]=6*a+j;ids[j+6]=6*b+j;ids[j+12]=6*obj+j;}
   for(int i=selected.first;i<=selected.last;++i){double s=(i+.5)/grids[edge].count;auto pp=point(x,edge,s);regrip_birthlaw::ContactResult r;
    if(derivatives)r=regrip_birthlaw::evaluate(pp,object,old(edge,s),beforeLocal(edge,s),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue(),false);
    else{r=commitValue(x,edge,s);if(r.next.active){auto localForce=add(scale(r.next.normal,r.normalForce),scale(r.next.elastic,-tangentLineStiffness.getValue())),f=rotate(object.q,localForce),torque=cross(sub(pp.p,object.p),f);for(int j=0;j<3;++j){r.wrench.force[j]=f[j];r.wrench.force[j+6]=-f[j];r.wrench.force[j+9]=-torque[j];}}}
    if(!r.next.active)continue;
    if(r.degenerateEvent){++out.degenerate;out.unresolvedDepth=std::max(out.unresolvedDepth,r.unresolvedDepth);}
    out.a.energy+=weight*r.wrench.energy;out.D+=weight*r.plasticDissipation;out.elastic+=weight*r.elasticEnergy;out.capacity+=weight*r.capacity;if(r.next.sliding)out.slips++;else out.sticks++;double traction=tangentLineStiffness.getValue()*std::sqrt(dot(r.next.elastic,r.next.elastic));if(r.capacity>0)out.ratio=std::max(out.ratio,traction/r.capacity);out.a.contactForce+=weight*r.normalForce;out.a.contacts++;out.length+=weight;out.points.push_back({edge,s,weight,pp,r});
    if(derivatives){auto mapped=regrip_curved::map(pa,pb,s,L,r.wrench);for(int j=0;j<18;++j){forces[j]+=weight*mapped.force[j];for(int k=0;k<18;++k)block[j][k]+=weight*mapped.jacobian[18*j+k];}}
    else{auto f=regrip_curved::force(pa,pb,s,L,r.wrench);for(int j=0;j<18;++j)forces[j]+=weight*f[j];}
   }
   for(unsigned i=0;i<18;++i){out.a.f[ids[i]]+=forces[i];if(derivatives)for(unsigned j=0;j<18;++j)if(block[i][j])out.a.J.push_back({ids[i],ids[j],block[i][j]});}
  }check(out.a,x.size());return out;
 }
 Snapshot compute(const VecCoord&x)const{return evaluate(x,true);}
 Snapshot computeValue(const VecCoord&x)const{return evaluate(x,false);}
''')
# Class replacement changed substring of module name as well; set exact name.
source=source.replace('ReGripCurvedMaterialContact','ReGripCurvedContact')
Path(sys.argv[2]).write_text(source)
