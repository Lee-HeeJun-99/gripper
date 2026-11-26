"""Archive actual failed geometry attempts without deleting partial CAD."""
import json
from baseline_registry import ROOT,dump,ref

def main():
    messages={1:'wire pipe volume assertion failed before any exported parts',
              2:'adaptive wire volume failed: 43.28959115483572 versus 43.33063975819987 mm3',
              3:'separate pipe spans volume failed: 43.32996945857044 versus 43.33063975819987 mm3',
              4:'wire single-solid assertion failed; exact spans had two solids',
              5:'wire single-solid assertion failed; nominal face join did not cure mismatched beta radius'}
    for i,msg in messages.items():
        folder=ROOT/'cad/exports'/f'revAF_layout{i}';path=folder/'FAILED_EXECUTION.json'
        if path.exists():raise ValueError('Do not overwrite failed execution evidence')
        dump(path,dict(status='EXECUTION_FAIL',actually_executed=True,exit_code=1,
            command='drive_system_layout.py --tag revAF_layout'+str(i),error=msg,
            producer=ref(folder/'producer.py'),preserved_files=[ref(p) for p in sorted(folder.iterdir()) if p.is_file()],
            diagnosis='Wire radius was updated in wire_motion but its imported mechanism beta still used 4.75mm instead of actual 11.25mm idler radius. RevAF6 explicitly configures both. Previous failures retained.',
            whole_system_release=False))
    print('Recorded five actual failures; partial CAD kept, not regenerated or deleted')
if __name__=='__main__':main()
