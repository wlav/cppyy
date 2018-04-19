.. _features:

More Features
=============

.. toctree::
   :hidden:

   cppyy_features_header


The following is not meant to be an exhaustive list, but more of a show case.
Most features will be fairly obvious in their use.

The C++ code used for the examples below can be found
:doc:`here <cppyy_features_header>`, and it is assumed that that code is
loaded at the start of any session.
Download it, save it under the name ``features.h``, and load it:

  .. code-block:: python

    >>> import cppyy
    >>> cppyy.include('features.h')
    >>>


* **casting**: Is supposed to be unnecessary.
  Object pointer returns from functions provide the most derived class known
  in the hierarchy of the object being returned.
  This is important to preserve object identity as well as to make casting,
  a pure C++ feature after all, superfluous.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import Abstract, Concrete
    >>> c = Concrete()
    >>> Concrete.show_autocast.__doc__
    'Abstract* Concrete::show_autocast()'
    >>> d = c.show_autocast()
    >>> type(d)
    <class '__main__.Concrete'>
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
    >>> e = bind_object(addressof(d), Abstract)
    >>> type(e)
    <class '__main__.Abstract'>
    >>>


* **doc strings**: The doc string of a method or function contains the C++
  arguments and return types of all overloads of that name, as applicable.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import Concrete
    >>> print Concrete.array_method.__doc__
    void Concrete::array_method(int* ad, int size)
    void Concrete::array_method(double* ad, int size)
    >>>

* **enums**: Are translated as ints with no further checking.

* **memory**: C++ instances created by calling their constructor from python
  are owned by python.
  You can check/change the ownership with the __python_owns__ flag that every
  bound instance carries.
  Example:

  .. code-block:: python

    >>> from cppyy.gbl import Concrete
    >>> c = Concrete()
    >>> c.__python_owns__         # True: object created in Python
    True
    >>>

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

    >>> from cppyy.gbl import Concrete
    >>> print Concrete()
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

* **static methods**: Are represented as python's ``staticmethod`` objects
  and can be called both from the class as well as from instances.

* **strings**: The std::string class is considered a builtin C++ type and
  mixes quite well with python's str.
  Python's str can be passed where a ``const char*`` is expected, and an str
  will be returned if the return type is ``const char*``.

* **templated functions**: Automatically participate in overloading and are
  used in the same way as other global functions.

* **templated methods**: For now, require an explicit selection of the
  template parameters.
  This will be changed to allow them to participate in overloads as expected.

* **typedefs**: Are simple python references to the actual classes to which
  they refer.

* **unary operators**: Are supported if a python equivalent exists, and if the
  operator is defined in the C++ class.
