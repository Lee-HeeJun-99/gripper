import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_compiled_sources import identical_compiled_sources
old={'models/a/Kernel.h':'a','models/a/CMakeLists.txt':'b','models/a/input.json':'c','models/a/README.md':'old'}
new=dict(old);new['models/a/README.md']='new';new['models/a/NOTES.md']='added';assert identical_compiled_sources(old,new)
for key in ('models/a/Kernel.h','models/a/CMakeLists.txt','models/a/input.json'):
 changed=dict(new);changed[key]='changed';assert not identical_compiled_sources(old,changed)
changed=dict(new);changed['models/a/NewPhysics.cpp']='new';assert not identical_compiled_sources(old,changed)
print('PASS documentation-only evolution allowed;ALL modeled code/build/material inputs still exact')
