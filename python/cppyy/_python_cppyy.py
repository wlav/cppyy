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

# first load the dependency libraries of the backend, then
# pull in the libcppyy extension module
c = loader.load_cpp_backend()
import libcppyy as _backend
_backend._cpp_backend = c

# lookups on namespaces
# TODO: why here, and if so, how to share with PyPy/_cppyy?

### -----------------------------------------------------------------------------
### -- metaclass helper from six ------------------------------------------------
### -- https://bitbucket.org/gutworth/six/src/8a545f4e906f6f479a6eb8837f31d03731597687/six.py?at=default#cl-800
#
# Copyright (c) 2010-2015 Benjamin Peterson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


### template support ------------------------------------------------------------
# TODO: why is this necessary?? And if so, can it be shared with PyPy/_cppyy?
class Template:
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

class _stdmeta(type):
    def __getattr__(cls, name):     # for non-templated classes in std
        try:
          # TODO: why only classes here?
            klass = _backend.CreateScopeProxy(name, cls)
        except TypeError as e:
            raise AttributeError(str(e))
        setattr( cls, name, klass )
        return klass


#- exports -------------------------------------------------------------------
class gbl(with_metaclass(_ns_meta)):
    class std(with_metaclass(_stdmeta, object)):
      # pre-get string to ensure disambiguation from python string module
        string = _backend.CreateScopeProxy('string')

addressof = _backend.addressof
bind_object = _backend.bind_object

def load_reflection_info(name):
    sc = gbl.gSystem.Load(name)
    if sc == -1:
        raise RuntimeError("missing reflection library "+name)
