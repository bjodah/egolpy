from functools import wraps

def memoize(f):
    """
    Decorator to enable caching for computationally heavy functions
    """
    cache={}
    @wraps(f)
    def wrapper(*args):
        if args not in cache:
            cache[args]=f(*args)
        return cache[args]
    return wrapper


class ExtendedInitDecoratorFactory(object):
    """
    Bound __init__ method decorator for adding kwargs to derived
    class and extending
    """
    def __init__(self, superclass, **intercept_kwargs):
        self._superclass      = superclass
        self.intercept_kwargs = intercept_kwargs

    def __call__(self, init):
        @wraps(init)
        def wrapper(_self, *args, **kwargs):
            intercepted_kwargs = {}
            for key, value in self.intercept_kwargs.iteritems():
                if key in kwargs:
                    intercepted_kwargs[key] = kwargs.pop(key)
                else:
                    intercepted_kwargs[key] = value
            init(_self, **intercepted_kwargs) # Need _self here?
            #_self.__init__( ** intercepted_kwargs)
            self._superclass.__init__(_self, *args, **kwargs)

        wrapper.__name__ = init.__name__
        cur_doc = init.__doc__
        super_doc = self._superclass.__init__.__doc__
        if cur_doc != None or super_doc != None:
            if cur_doc == None: cur_doc = ''
            if super_doc == None: super_doc = ''
            wrapper.__doc__ = cur_doc + '\n Docstring of overloaded init: \n'+\
                          super_doc
        return wrapper

# SimpleCounter for use with shedskin (incompatible with numpy ndarray as of now)
# from collections import defaultdict
# class SimpleCounter(dict):
#     # def __new__(cls, *args):
#     #     return defaultdict.__new__(cls, int)

#     def __init__(self, iterable = ()):
#         d = dict([(x, iterable.count(x)) for x in set(iterable)])
#         self.__dict__ = d

#     def __missing__(self, key):
#         return 0
# Counter = SimpleCounter

# Shedskin workaround for Logging
# class Logger(object):
#     def info(self, msg):
#         print(msg)
#     def debug(self, msg):
#         print(msg)

# class logging(object):
#     def basicConfig(self):
#         pass
#     def getLogger(self, name):
#         return Logger(name)
#     def setLevel(self):
#         pass
#
