.. _classes:

.. role:: toconly
   :class: toconly


Classes
=======

Both Python and C++ support object-oriented code through classes and thus
it is logical to expose C++ classes as Python ones, including the full
inheritance hierarchy.

The C++ code used for the examples below can be found
:doc:`here <cppyy_features_header>`, and it is assumed that that code is
loaded at the start of any session.
Download it, save it under the name ``features.h``, and load it:

  .. code-block:: python

    >>> import cppyy
    >>> cppyy.include('features.h')
    >>>


All bound C++ code starts off from the global C++ namespace, represented in
Python by ``gbl``.
This namespace, as any other namespace, is treated as a module after it has
been loaded.
Thus, we can import C++ classes that live underneath it:

  .. code-block:: python

    >>> from cppyy.gbl import Concrete
    >>> Concrete
    <class cppyy.gbl.Concrete at 0x2058e30>
    >>>

Placing classes in the same structure as imposed by C++ guarantees identity,
even if multiple Python modules bind the same class.
There is, however, no necessity to expose that structure to end-users: when
developing a Python package that exposes C++ classes through ``cppyy``,
consider ``cppyy.gbl`` an "internal" module, and expose the classes in any
structure you see fit.
The C++ names will continue to follow the C++ structure, however, as is needed
for e.g. pickling:

  .. code-block:: python

    >>> from cppyy.gbl import Namespace
    >>> Concrete == Namespace.Concrete
    False
    >>> n = Namespace.Concrete.NestedClass()
    >>> type(n)
    <class cppyy.gbl.Namespace.Concrete.NestedClass at 0x22114c0>
    >>> type(n).__name__
    NestedClass
    >>> type(n).__module__
    cppyy.gbl.Namespace.Concrete
    >>> type(n).__cppname__
    Namespace::Concrete::NestedClass
    >>>

A bound C++ class *is* a Python class and can be used in any way a Python
class can.
For example, we can ask for ``help()``:

  .. code-block:: python

    >>> help(Concrete)
    Help on class Concrete in module gbl:

    class Concrete(Abstract)
     |  Method resolution order:
     |      Concrete
     |      Abstract
     |      CPPInstance
     |      __builtin__.object
     |
     |  Methods defined here:
     |
     |  __assign__(self, const Concrete&)
     |      Concrete& Concrete::operator=(const Concrete&)
     |
     |  __init__(self, *args)
     |      Concrete::Concrete(int n = 42)
     |      Concrete::Concrete(const Concrete&)
     |
     etc. ....


:toconly:`Inheritance`
""""""""""""""""""""""

The output of help shows the inheritance hierarchy, constructors, public
methods, and public data.
For example, ``Concrete`` inherits from ``Abstract`` and it has
a constructor that takes an ``int`` argument, with a default value of 42.
Consider:

  .. code-block:: python

    >>> from cppyy.gbl import Abstract
    >>> issubclass(Concrete, Abstract)
    True
    >>> a = Abstract()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
    TypeError: cannot instantiate abstract class 'Abstract'
    >>> c = Concrete()
    >>> isinstance(c, Concrete)
    True
    >>> isinstance(c, Abstract)
    True
    >>> d = Concrete(13)
    >>>

Just like in C++, interface classes that define pure virtual methods, such
as ``Abstract`` does, can not be instantiated, but their concrete
implementations can.
As the output of ``help`` showed, the ``Concrete`` constructor takes
an integer argument, that by default is 42.
The ``Concrete`` instances have a public data member ``m_int`` that
is treated as a Python property, albeit a typed one:

  .. code-block:: python

    >>> c.m_int, d.m_int
    (42, 13)
    >>> c.m_int = 3.14   # a float does not fit in an int
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: int/long conversion expects an integer object
    >>> c.m_int = int(3.14)
    >>> c.m_int, d.m_int
    (3, 13)
    >>>

Note that private and protected data members are not accessible and C++
const-ness is respected:

  .. code-block:: python

    >>> c.m_const_int = 71    # declared 'const int' in class definition
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: assignment to const data not allowed
    >>>

:toconly:`Methods`
""""""""""""""""""

C++ methods are represented as Python ones: these are first-class objects and
can be bound to an instance.
If a method is virtual in C++, the proper concrete method is called, whether
or not the concrete class is bound.
Similarly, if all classes are bound, the normal Python rules apply:

  .. code-block:: python

    >>> c.abstract_method()
    called Concrete::abstract_method
    >>> c.concrete_method()
    called Concrete::concrete_method
    >>> m = c.abstract_method
    >>> m()
    called Concrete::abstract_method
    >>>
