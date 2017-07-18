Features
========

.. toctree::
   :hidden:

   cppyy_features_header

The following is not meant to be an exhaustive list, but more of a show case.
Most features will be fairly obvious: classes are classes with inheritance
trees preserved, functions are functions, etc.

C++ features are mapped onto Python in a way that is natural to C++ to prevent
name clashes, duplication, and other ambiguities when mixing several large C++
code bases.
This can lead to a loss of "Pythonic feel."
A "pythonization" API is available to make C++ classes more pythonic in an
semi-automated way.
Some common classes, such as the Standard Templated Library (STL), have already
been pythonized.
Certain user-provided classes, such as smart pointers, are recognized and
automatically pythonized as well.

The example C++ code used can be found :doc:`here <cppyy_features_header>`.

* **abstract classes**: Are represented as Python classes, since they are
  needed to complete the inheritance hierarchies, but will raise a
  ``TypeError`` exception if an attempt is made to instantiate from them.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import AbstractClass, ConcreteClass
    >>> a = AbstractClass()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
    TypeError: cannot instantiate abstract class 'AbstractClass'
    >>> issubclass(ConcreteClass, AbstractClass)
    True
    >>> c = ConcreteClass()
    >>> isinstance(c, AbstractClass)
    True
    >>>

* **arrays**: Supported for builtin data types only, as used from module
  ``array`` (or any other builtin-type array that implements the Python buffer
  interface).
  Out-of-bounds checking is limited to those cases where the size is known at
  compile time.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> from array import array
    >>> c = ConcreteClass()
    >>> c.array_method(array('d', [1., 2., 3., 4.]), 4)
    1 2 3 4
    >>> c.m_data[4] # static size is 4, so out of bounds
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    IndexError: buffer index out of range
    >>>

* **builtin data types**: Map onto the expected equivalent python types, with
  the caveats that there may be size differences, different precision or
  rounding.
  For example, a C++ ``float`` is returned as a Python ``float``, which is in
  fact a C++ ``double``.
  As another example, a C++ ``unsigned int`` becomes a Python ``long``, but
  unsigned-ness is still honored:

  .. code-block:: python

    >>> type(cppyy.gbl.gUint)
    <type 'long'>
    >>> cppyy.gbl.gUint = -1
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: cannot convert negative integer to unsigned
    >>>

* **casting**: Is supposed to be unnecessary.
  Object pointer returns from functions provide the most derived class known
  in the hierarchy of the object being returned.
  This is important to preserve object identity as well as to make casting,
  a pure C++ feature after all, superfluous.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import AbstractClass, ConcreteClass
    >>> c = ConcreteClass()
    >>> ConcreteClass.show_autocast.__doc__
    'AbstractClass* ConcreteClass::show_autocast()'
    >>> d = c.show_autocast()
    >>> type(d)
    <class '__main__.ConcreteClass'>
    >>>

  As a consequence, if your C++ classes should only be used through their
  interfaces, then no bindings should be provided to the concrete classes
  (e.g. by excluding them using a :ref:`selection file <selection-files>`).
  Otherwise, more functionality will be available in Python than in C++.

  Sometimes you really, absolutely, do need to perform a cast.
  For example, if the instance is bound by another tool or even a 3rd party,
  hand-written, extension library.
  Assuming the object supports the ``CObject`` abstraction, then a C++-style
  reinterpret_cast (i.e. without implicitly taking offsets into account),
  can be done by taking and rebinding the address of an object:

  .. code-block:: python

    >>> from cppyy import addressof, bind_object
    >>> e = bind_object(addressof(d), AbstractClass)
    >>> type(e)
    <class '__main__.AbstractClass'>
    >>>

* **classes and structs**: Get mapped onto Python classes, where they can be
  instantiated as expected.
  If classes are inner classes or live in a namespace, their naming and
  location will reflect that.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass, Namespace
    >>> ConcreteClass == Namespace.ConcreteClass
    False
    >>> n = Namespace.ConcreteClass.NestedClass()
    >>> type(n)
    <class '__main__.Namespace::ConcreteClass::NestedClass'>
    >>>

* **data members**: Public data members are represented as Python properties
  and provide read and write access on instances as expected.
  Private and protected data members are not accessible, const-ness is
  respected.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> c = ConcreteClass()
    >>> c.m_int
    42
    >>> c.m_const_int = 71    # declared 'const int' in class definition
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: assignment to const data not allowed
    >>>

* **default arguments**: C++ default arguments work as expected, but python
  keywords are not supported.
  It is technically possible to support keywords, but for the C++ interface,
  the formal argument names have no meaning and are not considered part of the
  API, hence it is not a good idea to use keywords.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> c = ConcreteClass()       # uses default argument
    >>> c.m_int
    42
    >>> c = ConcreteClass(13)
    >>> c.m_int
    13
    >>>

* **doc strings**: The doc string of a method or function contains the C++
  arguments and return types of all overloads of that name, as applicable.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> print ConcreteClass.array_method.__doc__
    void ConcreteClass::array_method(int*, int)
    void ConcreteClass::array_method(double*, int)
    >>>

* **enums**: Are translated as ints with no further checking.

* **functions**: Work as expected and live in their appropriate namespace
  (which can be the global one, ``cppyy.gbl``).

* **inheritance**: All combinations of inheritance on the C++ (single,
  multiple, virtual) are supported in the binding.
  However, new python classes can only use single inheritance from a bound C++
  class.
  Multiple inheritance would introduce two "this" pointers in the binding.
  This is a current, not a fundamental, limitation.
  The C++ side will not see any overridden methods on the python side, as
  cross-inheritance is planned but not yet supported.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> help(ConcreteClass)
    Help on class ConcreteClass in module __main__:

    class ConcreteClass(AbstractClass)
     |  Method resolution order:
     |      ConcreteClass
     |      AbstractClass
     |      cppyy.CPPObject
     |      __builtin__.CPPInstance
     |      __builtin__.object
     |
     |  Methods defined here:
     |
     |  ConcreteClass(self, *args)
     |      ConcreteClass::ConcreteClass(const ConcreteClass&)
     |      ConcreteClass::ConcreteClass(int)
     |      ConcreteClass::ConcreteClass()
     |
     etc. ....

* **memory**: C++ instances created by calling their constructor from python
  are owned by python.
  You can check/change the ownership with the _python_owns flag that every
  bound instance carries.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> c = ConcreteClass()
    >>> c._python_owns            # True: object created in Python
    True
    >>>

* **methods**: Are represented as python methods and work as expected.
  They are first class objects and can be bound to an instance.
  Virtual C++ methods work as expected.
  To select a specific virtual method, do like with normal python classes
  that override methods: select it from the class that you need, rather than
  calling the method on the instance.
  To select a specific overload, use the __dispatch__ special function, which
  takes the name of the desired method and its signature (which can be
  obtained from the doc string) as arguments.

* **namespaces**: Are represented as python classes.
  Namespaces are more open-ended than classes, so sometimes initial access may
  result in updates as data and functions are looked up and constructed
  lazily.
  Thus the result of ``dir()`` on a namespace shows the classes available,
  even if they may not have been created yet.
  It does not show classes that could potentially be loaded by the class
  loader.
  Once created, namespaces are registered as modules, to allow importing from
  them.
  Namespace currently do not work with the class loader.
  Fixing these bootstrap problems is on the TODO list.
  The global namespace is ``cppyy.gbl``.

* **NULL**: Is represented as ``cppyy.gbl.nullptr``.
  In C++11, the keyword ``nullptr`` is used to represent ``NULL``.
  For clarity of intent, it is recommended to use this instead of ``None``
  (or the integer ``0``, which can serve in some cases), as ``None`` is better
  understood as ``void`` in C++.

* **operator conversions**: If defined in the C++ class and a python
  equivalent exists (i.e. all builtin integer and floating point types, as well
  as ``bool``), it will map onto that python conversion.
  Note that ``char*`` is mapped onto ``__str__``.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import ConcreteClass
    >>> print ConcreteClass()
    Hello operator const char*!
    >>>

* **operator overloads**: If defined in the C++ class and if a python
  equivalent is available (not always the case, think e.g. of ``operator||``),
  then they work as expected.
  Special care needs to be taken for global operator overloads in C++: first,
  make sure that they are actually reflected, especially for the global
  overloads for ``operator==`` and ``operator!=`` of STL vector iterators in
  the case of gcc (note that they are not needed to iterate over a vector).
  Second, make sure that reflection info is loaded in the proper order.
  I.e. that these global overloads are available before use.

* **pointers**: For builtin data types, see arrays.
  For objects, a pointer to an object and an object looks the same, unless
  the pointer is a data member.
  In that case, assigning to the data member will cause a copy of the pointer
  and care should be taken about the object's life time.
  If a pointer is a global variable, the C++ side can replace the underlying
  object and the python side will immediately reflect that.

* **PyObject***: Arguments and return types of ``PyObject*`` can be used, and
  passed on to CPython API calls.
  Since these CPython-like objects need to be created and tracked (this all
  happens through ``cpyext``) this interface is not particularly fast.

* **static data members**: Are represented as python property objects on the
  class and the meta-class.
  Both read and write access is as expected.

* **static methods**: Are represented as python's ``staticmethod`` objects
  and can be called both from the class as well as from instances.

* **strings**: The std::string class is considered a builtin C++ type and
  mixes quite well with python's str.
  Python's str can be passed where a ``const char*`` is expected, and an str
  will be returned if the return type is ``const char*``.

* **templated classes**: Are represented in a meta-class style in python.
  This may look a little bit confusing, but conceptually is rather natural.
  For example, given the class ``std::vector<int>``, the meta-class part would
  be ``std.vector``.
  Then, to get the instantiation on ``int``, do ``std.vector(int)`` and to
  create an instance of that class, do ``std.vector(int)()``:

  .. code-block:: python

    >>> import cppyy
    >>> cppyy.load_reflection_info('libexampleDict.so')
    >>> cppyy.gbl.std.vector                # template metatype
    <cppyy.CppyyTemplateType object at 0x00007fcdd330f1a0>
    >>> cppyy.gbl.std.vector(int)           # instantiates template -> class
    <class '__main__.std::vector<int>'>
    >>> cppyy.gbl.std.vector(int)()         # instantiates class -> object
    <__main__.std::vector<int> object at 0x00007fe480ba4bc0>
    >>>

  Note that templates can be build up by handing actual types to the class
  instantiation (as done in this vector example), or by passing in the list of
  template arguments as a string.
  The former is a lot easier to work with if you have template instantiations
  using classes that themselves are templates in  the arguments (think e.g a
  vector of vectors).
  All template classes must already exist in the loaded reflection info, they
  do not work (yet) with the class loader.

  For compatibility with other bindings generators, use of square brackets
  instead of parenthesis to instantiate templates is supported as well.

* **templated functions**: Automatically participate in overloading and are
  used in the same way as other global functions.

* **templated methods**: For now, require an explicit selection of the
  template parameters.
  This will be changed to allow them to participate in overloads as expected.

* **typedefs**: Are simple python references to the actual classes to which
  they refer.

* **unary operators**: Are supported if a python equivalent exists, and if the
  operator is defined in the C++ class.
