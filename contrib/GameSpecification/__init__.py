# UPDATE 'contrib'
from contrib.autodetect import search_path_for_subclasses

from importlib import import_module

# UPDATE these:
pkg_loc   = 'contrib/'
classname = 'GameSpecification'

classpath = pkg_loc+classname
subclasses = search_path_for_subclasses(classpath)

pkgmodprefix = pkg_loc.replace('/','.')+classname+'.'

BaseClass  = import_module(pkgmodprefix+'BaseClass')
baseclass  = BaseClass.__dict__[classname]

__all__ = ["BaseClass"]

for modname in [x.split('_')[0] for x in subclasses.keys()]:
    import_module(pkgmodprefix+modname)
    __all__.extend(modname)

