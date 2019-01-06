.. _installation:

Installation
============

The ``cppyy`` module and its dependencies are available through `PyPI`_ for
both CPython (2 and 3) and PyPy (5.9.0 and later).
The cleanest/easiest way to install cppyy is using `virtualenv`_ and pip::

  $ virtualenv WORK
  $ source WORK/bin/activate
  (WORK) $ pip install cppyy

The use of virtualenv allows you to easily wipe out the full isntallation by
removing the virtualenv directory::

  $ rm -rf WORK

Wheels for the backend are available for GNU/Linux, MacOS-X, and MS Windows
(support for MS Windows is in beta).
The Linux wheels are built on manylinux, but with gcc 5.5, not the 4.8.2 that
ships with manylinux, since ``cppyy`` exposes C++ APIs.
Using 4.8.2 would have meant that any software using ``cppyy`` would have to
be (re)compiled for the older gcc ABI, which the odds don't favor.
Note that building cppyy with 4.8.2 (and requiring the old ABI) works fine,
but would only support C++11.

The ``CPyCppyy`` and ``cppyy`` packages can not produce wheels as they must be
build locally in order to match the local compiler and system files and CPU
features (e.g. AVX).

The C++17 standard is the default for all wheels.
When building from source, the highest version among 17, 14, and 11 that your
native compiler supports will be chosen.
You can control the standard selection by setting the ``STDCXX`` envar to
'17', '14', or '11'.
When building from source, build-time only dependencies are ``cmake`` (for 
general build), ``python`` (obviously, but also for LLVM), and a modern C++
compiler (one that supports at least C++11).
You can "upgrade" to C++17 or "downgrade" to C++11 by setting the ``STDCXX``

Compilation of the backend, which contains a customized version of
Clang/LLVM, can take a long time, so by default the setup script will use all
cores (x2 if hyperthreading is enabled).
To change that behavior, set the MAKE_NPROCS environment variable to the
desired number of processes to use.
To see progress while waiting, use ``--verbose``::

 $ STDCXX=17 MAKE_NPROCS=32 pip install --verbose cppyy

The bdist_wheel of the backend is reused by pip for all versions of CPython
and PyPy, thus the long compilation is needed only once.
Unless you build on the manylinux1 docker images, wheels for
``cppyy-backend`` and for ``CPyCppyy`` are disabled, because ``setuptools``
(as used by ``pip``) does not properly resolve dependencies for wheels.
You will see a harmless error message to that effect fly by.

On Windows, some temporary path names may be too long and the build will fail
in that case.
To resolve, set the ``TMP`` and ``TEMP`` envars to something short, before
building.
For example::

 > set TMP=C:\TMP
 > set TEMP=C:\TMP

If you use the ``--user`` option to pip, make sure that the PATH envar points
to the bin directory that will contain the installed entry points during the
installation, as the build process needs them.
You may also need to install ``wheel`` first, if you have an older version of
pip.
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
