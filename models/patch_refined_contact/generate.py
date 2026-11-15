"""Independent immutable per-ELEMENT material resolution, not moving remapping.

The only constitutive-source change is the grid count selected during prepare.
All force,Jacobian,return,event and Commit functions stay byte-identical apart
from the independent component name. The original component is untouched.
"""
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text()


def once(old, new):
    global source
    if source.count(old) != 1:
        raise ValueError('unexpected frozen template: ' + old[:80])
    source = source.replace(old, new)


once('public:\n SOFA_CLASS', 'public:\n sofa::core::objectmodel::Data<sofa::type::vector<double>> edgeSpacing;\n SOFA_CLASS')
once(':EnergyField(s),\n segments', ':EnergyField(s),edgeSpacing(initData(&edgeSpacing,"edgeSpacing","Immutable per-element reference spacing mm;empty preserves original uniform grid")),\n segments')
once('for(auto i:segments.getValue())s.push_back(i);return s;', 'for(auto i:segments.getValue())s.push_back(i);for(double h:edgeSpacing.getValue())s.push_back(h);return s;')
once(' void prepare(const VecCoord&x){', '''
 double spacingForEdge(unsigned e)const{
  const auto&v=edgeSpacing.getValue();if(v.empty())return historySpacing.getValue();
  if(v.size()*2!=segments.getValue().size())throw std::invalid_argument("one spacing per reference element required");
  double h=v.at(e);if(!std::isfinite(h)||h<=0||h>1)throw std::invalid_argument("invalid immutable element spacing");
  return h;
 }
 void prepare(const VecCoord&x){''')
once('g.count=regrip_birth::materialCells(L,historySpacing.getValue());', 'g.count=regrip_birth::materialCells(L,spacingForEdge(i/2));')
once('  previous=x;rule=', '  std::cout<<"PATCH_GRID {\\"states\\":"<<total<<",\\"elements\\":"<<grids.size()<<"}\\n";\n  previous=x;rule=')
source = source.replace('CurvedMaterialContact', 'PatchRefinedContact').replace('ReGripCurvedContact', 'ReGripPatchRefinedContact')
Path(sys.argv[2]).write_text(source)
