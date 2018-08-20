.. _installation:

Installation
============

The ``cppyy`` module and its dependencies are available through `PyPI`_ for
both CPython (2 and 3) and PyPy (5.9.0 and later).
The cleanest/easiest way to install cppyy is using `virtualenv`_ and pip.
However, if you do install with pip on Linux, it will select the manylinux1
binary wheels.
Because the gcc compiler on manylinux1 is ancient (4.8.2), this will restrict
you to C++11.
Wheels also exist for Mac, where the default is C++14.

The alternative is to build from source.
Build-time only dependencies are ``cmake`` (for general build), ``python``
(also for LLVM), and a modern C++ compiler (one that supports at least
C++11).
By default, support for C++14 will be chosen.
You can "upgrade" to C++17 or "downgrade" to C++11 by setting the ``STDCXX``
envar to '17' or '11' respectively when building, assuming your compiler
supports it.

Compilation of the backend, which contains a customized version of
Clang/LLVM, can take a long time, so by default the setup script will use all
cores (x2 if hyperthreading is enabled).
To change that behavior, set the MAKE_NPROCS environment variable to the
desired number of processes to use.
To see progress while waiting, use ``--verbose``::

 $ STDCXX=17 MAKE_NPROCS=32 pip install --verbose cppyy

The bdist_wheel of the backend is reused by pip for all versions of CPython
and PyPy, thus the long compilation is needed only once.

If you use the ``--user`` option to pip, make sure that the PATH envar points
to the bin directory that will contain the installed entry points during the
installation, as the build process needs them.
You may also need to install wheel first.
Example::

 $ pip install wheel --user
 $ PATH=$HOME/.local/bin:$PATH pip install cppyy --user

PyPy 5.7 and 5.8 have a built-in module ``cppyy``.
You can still install the ``cppyy`` package, but the built-in module takes
precedence.
To use ``cppyy``, first import a compatibility module::

 $ pypy
 [PyPy 5.8.0 with GCC 5.4.0] on linux2
 >>>> import cppyy_compat, cppyy
 >>>>

You will have to set ``LD_LIBRARY_PATH`` appropriately if you get an
``EnvironmentError`` (it will indicate the needed directory).

Note that your python interpreter (whether CPython or ``pypy-c``) may not have
been linked by the C++ compiler.
This can lead to problems during loading of C++ libraries and program shutdown.
In that case, re-linking is highly recommended.

Older versions of PyPy (5.6.0 and earlier) have a built-in ``cppyy`` based on
`Reflex`_, which is less feature-rich and no longer supported.
However, both the :doc:`distribution tools <dictionaries>` and user-facing
Python codes are very backwards compatible.

.. _`PyPI`: https://pypi.python.org/pypi/cppyy/
.. _`virtualenv`: https://pypi.python.org/pypi/virtualenv
.. _`are available`: https://cern.ch/wlav/wheels/
.. _`Reflex`: https://root.cern.ch/how/how-use-reflex
