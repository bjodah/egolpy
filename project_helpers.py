class ExtendedInitDecoratorFactory(object):
    """
    Bound __init__ method decorator for adding kwargs to derived
    class and extending
    """
    def __init__(self, superclass, **intercept_kwargs):
        self._superclass      = superclass
        self.intercept_kwargs = intercept_kwargs

    def __call__(self, init):

        def wrapper(_self, *args, **kwargs):
            intercepted_kwargs = {}
            for key, value in self.intercept_kwargs.iteritems():
                if key in kwargs:
                    intercepted_kwargs[key] = kwargs.pop(key)
                else:
                    intercepted_kwargs[key] = value
            self._superclass.__init__(_self, *args, **kwargs)
            init(_self, **intercepted_kwargs) # Need _self here?
        wrapper.__name__ = init.__name__
        cur_doc = init.__doc__
        super_doc = self._superclass.__init__.__doc__
        if cur_doc != None or super_doc != None:
            if cur_doc == None: cur_doc = ''
            if super_doc == None: super_doc = ''
            wrapper.__doc__ = cur_doc + '\n Docstring of overloaded init: \n'+\
                          super_doc
        return wrapper
