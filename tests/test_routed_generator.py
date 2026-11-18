"""Guarded source specialization preserves originals;not a physics certificate."""
import tempfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from film_routed_generate import generate
from curve_common import sha
def fixture(path):
 for name in ('models/film_rail_tendon/Kernel.h','models/film_rail_tendon/FilmRailTendon.cpp','models/film_routed_tendon/Route.h','tests/test_film_rail_tendon_api.cpp'):
  dest=path/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
for optimized in (False,True):
 with tempfile.TemporaryDirectory(prefix='routed_generator_',dir=ROOT/'build') as temporary:
  path=Path(temporary);fixture(path);original={name:sha(path/name) for name in ('models/film_rail_tendon/Kernel.h','models/film_rail_tendon/FilmRailTendon.cpp','tests/test_film_rail_tendon_api.cpp')};result=generate(path,core_only=optimized)
  assert all(sha(path/name)==digest for name,digest in original.items())
  assert result['core_only']==optimized
  if optimized:
   core=(path/'models/film_routed_tendon/Core.generated.h').read_text();assert 'shell_AD_and_dispatch' in core and 'attachment_AD_and_dispatch' in core and 'contact_AD_and_dispatch' in core and 'tendon_AD_and_dispatch' not in core
   assert 'CoreAssembly(m).elements(u,0,' in (path/'models/film_routed_tendon/Route.h').read_text()
  try:generate(path,core_only=optimized)
  except ValueError:pass
  else:raise AssertionError('generated output silently overwritten')
print('PASS original bytes preserved,core specialization anchors,all core terms retained,output overwrite rejected;NOT physics/speed qualification')
