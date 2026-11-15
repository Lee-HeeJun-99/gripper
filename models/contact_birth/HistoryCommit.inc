 // Boundary values are physical limits, NEVER a small-denominator patch.
 regrip_history::History old(unsigned edge,double s)const{
  const auto&g=grids[edge];auto range=interval(previous,edge);regrip_history::History h;
  if(!range.active()||s<range.lo||s>range.hi)return h;
  auto p=point(previous,edge,s),o=pose(previous[objectIndex.getValue()]);h.local=rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));auto geo=regrip_history::geometry(regrip_history::constantV<regrip_history::First>(h.local),shape.getValue(),radius.getValue(),halfHeight.getValue());
  // At a true SDF boundary, zero normal capacity implies zero elastic limit.
  if(geo.distance.v>=pointRadius.getValue())return h;
  h.active=true;for(int j=0;j<3;++j)h.normal[j]=geo.normal[j].v;
  double t=s*g.count;unsigned a=std::min(unsigned(t),g.count-1);double l=std::max(double(a)/g.count,range.lo),u=std::min(double(a+1)/g.count,range.hi);
  if(!(u>l))return h; // zero-length intersection has zero extension limit
  double alpha=(s-l)/(u-l);V el{},eu{};
  if(l==double(a)/g.count&&g.state[a].active)el=regrip_history::transport(g.state[a].elastic,g.state[a].normal,h.normal);
  if(u==double(a+1)/g.count&&g.state[a+1].active)eu=regrip_history::transport(g.state[a+1].elastic,g.state[a+1].normal,h.normal);
  h.elastic=add(scale(el,1-alpha),scale(eu,alpha));return h;
 }
 V beforeLocal(unsigned edge,double s)const{auto p=point(previous,edge,s),o=pose(previous[objectIndex.getValue()]);return rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));}
 regrip_birthlaw::ContactResult query(const VecCoord&x,unsigned edge,double s,bool tangent)const{
  auto p=point(x,edge,s),o=pose(x[objectIndex.getValue()]);
  if(!tangent)return regrip_history::evaluateContact(p,o,{},shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),0.);
  return regrip_birthlaw::evaluate(p,o,old(edge,s),beforeLocal(edge,s),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue(),true);
 }
 regrip_birthlaw::ContactResult commitValue(const VecCoord&x,unsigned e,double s)const{return regrip_birthlaw::value(point(x,e,s),pose(x[objectIndex.getValue()]),old(e,s),beforeLocal(e,s),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue());}
 double lastEventTime=-std::numeric_limits<double>::infinity();
 unsigned unresolvedEvents=0;double maximumUnresolvedDepth=0;
 ~BirthAwareContact()override{std::cout<<std::setprecision(17)<<"BIRTH_EVENT_STATS {\"commits\":"<<steps<<",\"unresolved_samples\":"<<unresolvedEvents<<",\"maximum_unresolved_depth_mm\":"<<maximumUnresolvedDepth<<"}\n";}
 // Conservative per-material-node broadphase for the DEFINED relative chord.
 // No claim of exact surface CCD between these material samples.
 void checkTemporal(const VecCoord&x)const{
  auto currentObject=pose(x[objectIndex.getValue()]);
  for(unsigned e=0;e<grids.size();++e){auto a0=beforeLocal(e,0),b0=beforeLocal(e,1);auto a1=regrip_closure::localPoint(point(x,e,0),point(x,e,1),currentObject,0),b1=regrip_closure::localPoint(point(x,e,0),point(x,e,1),currentObject,1);double motion=std::max(std::sqrt(dot(sub(a1,a0),sub(a1,a0))),std::sqrt(dot(sub(b1,b0),sub(b1,b0))));if(motion<1e-14)continue;
   auto range=regrip_closure::activeInterval(a0,b0,shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue()+motion);if(!range.active())continue;const auto&g=grids[e];unsigned lo=unsigned(std::ceil(range.lo*g.count)),hi=std::min(g.count,unsigned(std::floor(range.hi*g.count)));
   for(unsigned i=lo;i<=hi;++i){double s=double(i)/g.count;auto p=add(scale(a0,1-s),scale(b0,s)),q=add(scale(a1,1-s),scale(b1,s));if(regrip_closure::sdf(p,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue()&&regrip_closure::sdf(q,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue())regrip_birthlaw::transientDepth(p,q,shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue());}
  }
 }
