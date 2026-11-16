"""Independent exact-function history adapter; immutable parent generators."""
import sys
from pathlib import Path
source = Path(sys.argv[1]).read_text().replace('CurvedMaterialContact', 'GeneralVectorCurvedContact').replace('ReGripCurvedContact', 'ReGripGeneralVectorContact')
a = source.index(' regrip_history::History old(')
b = source.index(' V beforeLocal(', a)
source = source[:a] + '''
 std::vector<regrip_general_history::Owner> owners;
 regrip_history::History old(unsigned edge,double s)const{
  return owners.empty()?regrip_history::History{}:owners.at(edge).at(s);
 }
''' + source[b:]
# Freeze endpoint geometry by VALUE, never capture mutable field/x references.
needle = '  committedPlastic+=increment;released+=detach;previous=x;cachedEpoch=~0u;'
assert source.count(needle) == 1
source = source.replace(needle, '''
  if(owners.empty())owners.resize(grids.size());
  std::vector<regrip_general_history::Owner::Trial> trials;
  regrip_general_history::Owner::Physics physics{shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue()};
  for(unsigned e=0;e<grids.size();++e){
   unsigned a=segments.getValue()[2*e],b=segments.getValue()[2*e+1];double L=grids[e].length;
   auto frozen=[L](Pose left,Pose right){return [L,left,right](double s){Pose p;p.p=regrip_curved::position(left,right,s,L);return p;};};
   trials.push_back(owners[e].trial(frozen(pose(previous[a]),pose(previous[b])),frozen(pose(x[a]),pose(x[b])),pose(previous[objectIndex.getValue()]),pose(x[objectIndex.getValue()]),physics));
  }
  for(unsigned e=0;e<owners.size();++e)owners[e].commit(trials[e]);
''' + needle)
if len(sys.argv)>3 and sys.argv[3]in ('gauss','adaptive'):
    # Same immutable material quadrature for force, Jacobian, energy and Commit.
    # State storage remains a FUNCTION, not values at these quadrature nodes.
    source=source.replace(' regrip_history::History old(', '''
 std::vector<std::pair<double,double>> materialRule(unsigned e)const{
  std::vector<std::pair<double,double>> nodes;auto rule=regrip_closure::gauss(cellOrder.getValue());
  for(unsigned i=0;i<grids[e].count;++i)for(auto [x,w]:rule)
   nodes.push_back({(i+.5+.5*x)/grids[e].count,.5*w*grids[e].length/grids[e].count});
  return nodes;
 }
 regrip_history::History old(''',1)
    old='for(int i=selected.first;i<=selected.last;++i){double s=(i+.5)/grids[edge].count;auto pp='
    assert source.count(old)==1
    source=source.replace(old,'for(auto [s,weight]:materialRule(edge)){auto pp=')
    a=source.index(' void commit(const VecCoord&x){');b=source.index(' void init()override',a)
    source=source[:a]+'''
 void commit(const VecCoord&x){
  validateInput(x);checkTemporal(x);
  if(owners.empty())owners.resize(grids.size());
  std::vector<regrip_general_history::Owner::Trial> trials;
  regrip_general_history::Owner::Physics physics{shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue()};
  for(unsigned e=0;e<grids.size();++e){
   unsigned a=segments.getValue()[2*e],b=segments.getValue()[2*e+1];double L=grids[e].length;
   auto frozen=[L](Pose left,Pose right){return [L,left,right](double s){Pose p;p.p=regrip_curved::position(left,right,s,L);return p;};};
   trials.push_back(owners[e].trial(frozen(pose(previous[a]),pose(previous[b])),frozen(pose(x[a]),pose(x[b])),pose(previous[objectIndex.getValue()]),pose(x[objectIndex.getValue()]),physics));
  }
  double increment=0,detach=0;unsigned born=0,dead=0;
  for(unsigned e=0;e<grids.size();++e)for(auto [s,w]:materialRule(e)){
   auto prior=old(e,s);auto r=commitValue(x,e,s);
   increment+=w*r.plasticDissipation;
   if(prior.active&&!r.next.active){detach+=w*.5*tangentLineStiffness.getValue()*dot(prior.elastic,prior.elastic);++dead;}
   if(!prior.active&&r.next.active)++born;
  }
  for(unsigned e=0;e<owners.size();++e)owners[e].commit(trials[e]);
  committedPlastic+=increment;released+=detach;bornNodes+=born;deadNodes+=dead;
  previous=x;cachedEpoch=~0u;
 }
''' + source[b:]
    # The selected midpoint envelope and midpoint weight are not used here.
    source=source.replace('auto selected=bounds(interval(x,edge),grids[edge].count);','')
    source=source.replace('double L=grids[edge].length,weight=L/grids[edge].count;','double L=grids[edge].length;')
    if sys.argv[3]=='adaptive':
        a=source.index(' std::vector<std::pair<double,double>> materialRule(')
        b=source.index(' regrip_history::History old(',a)
        source=source[:a]+'''
 std::vector<std::pair<double,double>> materialRule(const VecCoord&x,unsigned e)const{
  return regrip_general_history::adaptiveMaterialRule(grids[e].count,grids[e].length,[&](double s){
   auto r=commitValue(x,e,s);auto prior=old(e,s);std::array<double,11> v{};
   v[0]=r.normalForce;v[1]=r.elasticEnergy;v[2]=r.plasticDissipation;
   auto o=pose(x[objectIndex.getValue()]);auto p=point(x,e,s);
   auto force=rotate(o.q,add(scale(r.next.normal,r.normalForce),scale(r.next.elastic,-tangentLineStiffness.getValue())));
   // For a sphere the normal line passes through the center EXACTLY.
   // Avoid refining roundoff from cross(r,Fn*r/|r|) as physical torque.
   // This changes only an error ESTIMATOR, never the assembled force/torque.
   auto momentForce=shape.getValue()==0?rotate(o.q,scale(r.next.elastic,-tangentLineStiffness.getValue())):force;
   auto torque=cross(sub(p.p,o.p),momentForce);
   for(int j=0;j<3;++j){v[3+j]=std::abs(force[j]);v[6+j]=std::abs(torque[j]);}
   v[9]=.5*tangentLineStiffness.getValue()*dot(prior.elastic,prior.elastic);
   v[10]=prior.active&&!r.next.active?v[9]:0;
   return v;
  });
 }
''' + source[b:]
        source=source.replace('materialRule(edge)','materialRule(x,edge)').replace('materialRule(e)','materialRule(x,e)')
Path(sys.argv[2]).write_text(source)
