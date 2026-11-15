"""Generate an independent fixed-material-point contrast, not an old-model edit."""
import sys
from pathlib import Path
def replace_section(text,begin,end,replacement):
    a=text.index(begin);b=text.index(end,a);return text[:a]+replacement+text[b:]
source=Path(sys.argv[1]).read_text().replace('BirthAwareContact','MaterialPointContact').replace('ReGripBirthContact','ReGripMaterialPointContact')
source=replace_section(source,' regrip_history::History old(',' V beforeLocal(',r'''
 double committedPlastic=0;
 struct Bounds{int first=0,last=-1;};
 Bounds bounds(const regrip_closure::Interval&r,unsigned count)const{
  if(!r.active())return {};
  return {std::max(0,int(std::ceil(r.lo*count-.5))),std::min(int(count)-1,int(std::floor(r.hi*count-.5)))};
 }
 regrip_history::History old(unsigned edge,double s)const{
  const auto&g=grids.at(edge);double coordinate=s*g.count-.5;long i=std::lround(coordinate);
  double bound=64*std::numeric_limits<double>::epsilon()*std::max(1.,double(g.count));
  if(i<0||i>=long(g.count)||std::abs(coordinate-i)>bound)throw std::invalid_argument("history query is not an immutable material point");
  return g.state[i];
 }
''')
# Both AD force and scalar end observation use EXACTLY the same fixed material
# abscissae and weights. Normal active-interval Gauss remains independent.
begin='   unsigned first='
end='   for(unsigned i=0;i<18;'
assert source.count(begin)==2
for _ in range(2):
    source=replace_section(source,begin,end,r'''
   auto selected=bounds(range,grids[edge].count);
   for(int i=selected.first;i<=selected.last;++i)sample((i+.5)/grids[edge].count,grids[edge].length/grids[edge].count,true);
''')
source=replace_section(source,' void commit(const VecCoord&x){',' void init()override',r'''
 void commit(const VecCoord&x){
  validateInput(x);checkTemporal(x);
  std::vector<std::vector<std::pair<unsigned,regrip_history::History>>>next(grids.size());
  double increment=0,detach=0;
  for(unsigned e=0;e<grids.size();++e){auto selected=bounds(interval(x,e),grids[e].count);const auto&g=grids[e];double weight=g.length/g.count;
   for(int i=selected.first;i<=selected.last;++i){auto r=commitValue(x,e,(i+.5)/g.count);increment+=weight*r.plasticDissipation;if(r.next.active)next[e].push_back({unsigned(i),r.next});}
   size_t j=0;for(unsigned i:g.active){while(j<next[e].size()&&next[e][j].first<i)++j;if(j==next[e].size()||next[e][j].first!=i)detach+=weight*.5*tangentLineStiffness.getValue()*dot(g.state[i].elastic,g.state[i].elastic);}
  }
  for(unsigned e=0;e<grids.size();++e){auto&g=grids[e];countTransitions(g,next[e]);for(unsigned i:g.active)g.state[i]={};g.active.clear();for(auto&v:next[e]){g.state[v.first]=v.second;g.active.push_back(v.first);}}
  committedPlastic+=increment;released+=detach;previous=x;cachedEpoch=~0u;
 }
''')
source=source.replace('g.state.resize(g.count+1)','g.state.resize(g.count)').replace('total+=g.count+1','total+=g.count')
# Temporal guard scans the same physical material points, never a moving
# quadrature index. Retain the explicit resolved-through-event rejection.
source=source.replace('unsigned lo=unsigned(std::ceil(range.lo*g.count)),hi=std::min(g.count,unsigned(std::floor(range.hi*g.count)));','auto selected=bounds(range,g.count);')
source=source.replace('for(unsigned i=lo;i<=hi;++i){double s=double(i)/g.count;','for(int i=selected.first;i<=selected.last;++i){double s=(i+.5)/g.count;')
source=source.replace('<<maximumUnresolvedDepth<<"}\\n"','<<maximumUnresolvedDepth<<",\\\"point_commit_plastic\\\":"<<committedPlastic<<",\\\"observer_plastic\\\":"<<plastic<<"}\\n"')
assert 'for(unsigned i=lo;i<=hi'not in source
Path(sys.argv[2]).write_text(source)
