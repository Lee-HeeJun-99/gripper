from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]
source=(root/'diagnostics/curved_contact/Invariants.cpp').read_text()
source=source.replace('#include "../../models/curved_contact/CurvedContact.cpp"','#include "'+str(root/'models/patch_refined_contact/RefinedContact.cpp')+'"').replace('CurvedMaterialContact','PatchRefinedContact')
needle='f->historySpacing.setValue(.02);'
if source.count(needle)!=1:raise ValueError('preserved invariant test changed')
source=source.replace(needle,needle+'f->edgeSpacing.setValue({.007});')
Path(sys.argv[1]).write_text(source)
