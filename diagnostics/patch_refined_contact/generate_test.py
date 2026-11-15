import sys
from pathlib import Path

root=Path(__file__).resolve().parents[2]
source=(root/'tests/test_curved_contact.cpp').read_text()
source=source.replace('#include "../models/curved_contact/CurvedContact.cpp"','#include "'+str(root/'models/patch_refined_contact/RefinedContact.cpp')+'"').replace('CurvedMaterialContact','PatchRefinedContact')
old='field->historySpacing.setValue(.02);field->prepare(x);'
new='field->historySpacing.setValue(.02);field->edgeSpacing.setValue({.01});field->prepare(x);require(field->grids.at(0).count==100,"explicit immutable element resolution");'
if source.count(old)!=1:raise ValueError('expected preserved API test source')
source=source.replace(old,new)
marker=' std::cout<<"PASS actual API FD="'
extra='''
 bool rejected=false;field->edgeSpacing.setValue({.02});try{field->compute(x);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"element resolution cannot change during trial");field->edgeSpacing.setValue({.01});
 for(auto spacing:std::vector<sofa::type::vector<double>>{{0.},{.01,.02},{1e-10}}){auto bad=sofa::core::objectmodel::New<PatchRefinedContact>(state.get());bad->segments.setValue({0,1});bad->objectIndex.setValue(2);bad->edgeSpacing.setValue(spacing);bool caught=false;try{bad->prepare(x);}catch(const std::invalid_argument&){caught=true;}require(caught,"invalid shape/zero/overbudget spacing rejected");}
'''
if source.count(marker)!=1:raise ValueError('expected API success marker')
source=source.replace(marker,extra+marker)
Path(sys.argv[1]).write_text(source)
