""" CPython-specific touch-ups
"""

from cppyy_backend import loader

__all__ = [
    'gbl',
    'addressof',
    'bind_object',
    'load_reflection_info',
    '_backend',
    ]

# first load the dependency libraries of the backend, then pull in the
# libcppyy extension module
c = loader.load_cpp_backend()
import libcppyy as _backend
_backend._cpp_backend = c


### template support ---------------------------------------------------------
class Template(object):  # expected/used by CPyCppyyHelpers.cxx in CPyCppyy
    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "<cppyy.Template '%s' object at %s>" % (self.__name__, hex(id(self)))

    def __call__(self, *args):
        newargs = [self.__name__]
        for arg in args:
            if type(arg) == str:
                arg = ','.join(map(lambda x: x.strip(), arg.split(',')))
            newargs.append(arg)
        result = _backend.MakeCppTemplateClass( *newargs )

      # special case pythonization (builtin_map is not available from the C-API)
        if 'push_back' in result.__dict__:
            def iadd(self, ll):
                [self.push_back(x) for x in ll]
                return self
            result.__iadd__ = iadd

        return result

    def __getitem__(self, *args):
        if args and type(args[0]) == tuple:
            return self.__call__(*(args[0]))
        return self.__call__(*args)

_backend.Template = Template


#- :: and std:: namespaces ---------------------------------------------------
class _ns_meta(type):
    def __getattr__(cls, name):
        try:
            attr = _backend.LookupCppEntity(name)
        except TypeError as e:
            raise AttributeError(str(e))
        if type(attr) is _backend.PropertyProxy:
            setattr(cls.__class__, name, attr)
            return attr.__get__(cls)
        setattr(cls, name, attr)
        return attr

class gbl(object):
    __metaclass__ = _ns_meta

    class std(object):
        __metaclass__ = _ns_meta

      # pre-get string to ensure disambiguation from python string module
        string = _backend.CreateScopeProxy('string')


#- exports -------------------------------------------------------------------
addressof = _backend.addressof
bind_object = _backend.bind_object

def load_reflection_info(name):
    sc = gbl.gSystem.Load(name)
    if sc == -1:
        raise RuntimeError("missing reflection library "+name)
