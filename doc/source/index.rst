.. cppyy documentation master file, created by
   sphinx-quickstart on Wed Jul 12 14:35:45 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cppyy: Automatic Python-C++ bindings
====================================

cppyy is an automatic Python-C++ bindings generator designed for large scale
programs in high performance computing that use modern C++.
Design and performance are described in this `PyHPC paper`_.

cppyy is based on `Cling`_, the C++ interpreter, to match Python's dynamism and
interactivity.
Consider this session, showing dynamic, interactive, mixing of C++ and Python
features:

.. code-block:: python

   >>> import cppyy
   >>> cppyy.cppdef("""
   ... class MyClass {
   ... public:
   ...     MyClass(int i) : m_data(i) {}
   ...     int m_data;
   ... };""")
   True
   >>> from cppyy.gbl import MyClass
   >>> m = MyClass(42)
   >>> cppyy.cppdef("""
   ... void say_hello(MyClass* m) {
   ...     std::cout << "Hello, the number is: " << m->m_data << std::endl;
   ... }""")
   True
   >>> MyClass.say_hello = cppyy.gbl.say_hello
   >>> m.say_hello()
   Hello, the number is: 42
   >>> m.m_data = 13
   >>> m.say_hello()
   Hello, the number is: 13
   >>>

cppyy seamlessly supports many advanced C++ features and is available for both
`CPython`_ and `PyPy`_, reaching C++-like performance with the latter.
cppyy makes judicious use of precompiled headers, dynamic loading, and lazy
instantiation, to support C++ programs consisting of millions of lines of code
and many thousands of classes.
cppyy minimizes dependencies to allow its use in distributed, heterogeneous,
development environments.

.. _Cling: https://root.cern.ch/cling
.. _`PyHPC paper`: http://conferences.computer.org/pyhpc/2016/papers/5220a027.pdf
.. _`CPython`: http://python.org
.. _`PyPy`: http://pypy.org


Contents:

.. toctree::
   :maxdepth: 2

   installation
   features
   distribution


Comments and bugs
-----------------

Please report bugs or requests for improvement on the `issue tracker`_.

.. _`issue tracker`: https://bitbucket.org/wlav/cppyy/issues
