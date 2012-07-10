import os, imp, importlib, sys
from glob import glob

import logging

logging.basicConfig()
logger = logging.getLogger('autodetect')
logger.setLevel(logging.DEBUG)


def search_path_for_subclasses(search_path):
    base_class_name = os.path.basename(search_path.strip('/'))
    pkg = '.'.join(search_path.strip('/').split('/'))+'.'
    # f, fname, desc = imp.find_module(pkg+'.BaseClass', ['.'])
    # mod = imp.load_module('BaseClass', f, fname, desc)
    mod = importlib.import_module(pkg+'BaseClass')
    cls = mod.__dict__[base_class_name]
    candidate_globs = ['*.py']
    ignore_startswith = ['__init__', 'BaseClass']
    candidate_paths = []
    main_path = os.path.dirname(sys.argv[0])
    for glb in candidate_globs:
        candidate_paths.extend(glob(os.path.join(main_path,
                                                 search_path,
                                                 glb)))
    for start in ignore_startswith:
        candidate_paths = [x for x in candidate_paths if \
                           not os.path.basename(x).startswith(start)]
    for candidate_path in candidate_paths:
        dirname =  os.path.dirname(candidate_path)
        basename = os.path.basename(candidate_path)
        modname, ext = os.path.splitext(basename)
        try:
            # f, fname, desc = imp.find_module(modname, [dirname])
            # mod = imp.load_module(modname, f, fname, desc)
            mod = importlib.import_module(pkg+modname)
            for k, v in mod.__dict__.items():
                if hasattr(v, '__mro__'):
                    if cls in v.__mro__ and v != cls:
                        logger.debug('Found subclass: {} {}'.format(\
                            k,v))
                        derived_modname = '_'.join(\
                            [os.path.splitext(basename)[0], k])
                        cls._subclasses[derived_modname] = v
        except ImportError:
            raise
    if cls._subclasses == {}:
        logger.debug('Found no subclasses for {}.'.format(cls))
    return cls._subclasses
