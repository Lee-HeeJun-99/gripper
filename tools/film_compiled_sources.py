"""Conservative ALL-model code/build/input closure;documentation is not compiled.

This does not filter to merely used headers:every modeled C++/CMake/JSON
input remains exact. No physics source difference is allowed for binary reuse.
"""
from pathlib import PurePosixPath
def compiled_sources(sources):
 return {name:digest for name,digest in sources.items() if PurePosixPath(name).suffix in ('.h','.hpp','.cpp','.cc','.c','.inl','.json','.cmake') or PurePosixPath(name).name=='CMakeLists.txt'}
def identical_compiled_sources(old,new):
 return compiled_sources(old)==compiled_sources(new)
