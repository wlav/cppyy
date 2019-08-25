.. _installation:

Installation
============

The installation requires a (modern) C++ compiler.
When using the wheels, minimally gcc5, clang5, or MSVC'17.
When installing from source, the only requirement is full support of C++11
(e.g. minimum gcc 4.8.1 on GNU/Linux), but older compilers than the ones
listed have not been tested.

The ``cppyy`` module and its dependencies are available through `PyPI`_ for
both CPython (2 and 3) and PyPy (5.9.0 and later), and through conda-forge.
The cleanest/easiest way to install cppyy is using `virtualenv`_ and pip::

  $ virtualenv WORK
  $ source WORK/bin/activate
  (WORK) $ python -m pip install cppyy

The use of virtualenv prevents pollution of any system directories and allows
you to wipe out the full installation simply by removing the virtualenv
created directory::

  $ rm -rf WORK

If you use anaconda, it is strongly recommended to use an the installation
`through conda-forge`_ and conda's environment manager.
Since the conda-forge packages are build from the PyPI releases, they may run
a bit behind.


Pre-compiled wheels
-------------------

Wheels for the backend (``cppyy-cling``) are available on PyPI for GNU/Linux,
MacOS-X, and MS Windows (both 32b and 64b).

The Linux wheels are built on manylinux, but with gcc 5.5, not the 4.8.2 that
ships with manylinux, since ``cppyy`` exposes C++ APIs.
Using 4.8.2 would have meant that any software using ``cppyy`` would have to
be (re)compiled for the older gcc ABI, which the odds don't favor.
Note that building cppyy fully with 4.8.2 (and requiring the old ABI across
the board) does work.

The wheels for MS Windows were build with MSVC Community Edition 2017.

There are no wheels for the ``CPyCppyy`` and ``cppyy`` packages, to allow
the C++ standard chosen to match the local compiler.


Conda
-----

Typical Python extension packages only expose a C interface for use through
the Python C-API.
Here, cppyy differs from regular packages because it exposes C++ APIs, among
others as part of its bootstrap.
Anaconda/miniconda and C++ do not mix well.
For example, on Linux, anaconda comes with the ancient gcc4.8.5, even as gcc
changed its ABI starting with gcc5, meaning that anaconda C++ binaries are not
ABI compatible with most current installations.
(That ABI change is why cppyy wheels on PyPI are build with gcc5.)
You *can* build and run cppyy with gcc4.8.5, and even use C++17, but you will
have to build it fully from source.

There is a set of more modern compilers available through conda-forge, but it
is only intended to be used through ``conda-build``.
In particular, it does not set up the corresponding run-time (it does install
it, for use through rpath).
For example, it adds the conda compilers to ``PATH`` but not their libraries
to ``LD_LIBRARY_PATH`` (Mac, Linux; MS Windows uses ``PATH`` for both
executables and libraries).
The upshot is that you will get the newer compilers and your system libraries
mixed in the same environment, unless you set ``LD_LIBRARY_PATH`` yourself,
e.g. by adding ``$CONDA_PREFIX/lib``.
That is, however, not recommended per the conda documentation.
Furthermore, the compilers pulled in from conda-forge are not their vanilla
distributions: header files have been modified.
This can lead to parsing problems if the system C library is too old.

Nevertheless, with the above caveats, if your system C++ libraries are new
enough, the following can be made to work::

 $ conda create -n WORK
 $ conda activate WORK
 (WORK) $ conda install python
 (WORK) $ conda install -c conda-forge compilers
 (WORK) [current compiler] $ python -m pip install cppyy


Switching C++ standard
----------------------

The C++17 standard is the default for Mac and Linux; but it is C++14 for
MS Windows (compiler limitation).
You can control the standard selection by setting the ``STDCXX`` envar to
'17', '14', or '11' (for Linux, the backend does not need to be recompiled),
but it will be lowered if your compiler does not support a newer standard.


Installing from source
----------------------
.. _installation_from_source:

The easiest way to install completely from source is again to use ``pip`` and
simply tell it to use the source package.
Build-time only dependencies are ``cmake`` (for general build), ``python``
(obviously, but also for LLVM), and a modern C++ compiler (one that supports
at least C++11).
Besides ``STDCXX`` to control the C++ standard version, you can use ``MAKE``
to change the ``make`` command and ``MAKE_NPROCS`` to control the maximum
number of parallel jobs.
For example (using ``--verbose`` to see progress)::

 $ STDCXX=17 MAKE_NPROCS=32 pip install --verbose cppyy --no-binary=cppyy-cling

Compilation of the backend, which contains a customized version of
Clang/LLVM, can take a long time, so by default the setup script will use all
cores (x2 if hyperthreading is enabled).

The bdist_wheel of the backend is reused by pip for all versions of CPython
and PyPy, thus the long compilation is needed only once for all different
versions of Python on the same machine.

Unless you build on the manylinux1 docker images, wheels for ``cppyy``,
``CPyCppyy``, and ``cppyy-backend`` are disabled, because ``setuptools``
(as used by ``pip``) does not properly resolve dependencies for wheels.
You will see a harmless "error" message to that effect fly by in the (verbose)
output.
You can force manual build of those wheels, as long as you make sure that you
have the proper dependencies *installed*, using ``--force-bdist``, when
building from the repository:
For example::

 $ git clone https://wlav@bitbucket.org/wlav/CPyCppyy.git
 $ cd CPyCppyy
 $ python setup.py bdist_wheel --force-bdist

On MS Windows, some temporary path names may be too long, causing the build to
fail.
To resolve this issue, set the ``TMP`` and ``TEMP`` envars to something short,
before building.
For example::

 > set TMP=C:\TMP
 > set TEMP=C:\TMP

If you use the ``--user`` option to ``pip`` and use ``pip`` directly on the
command line, make sure that the ``PATH`` envar points to the bin directory
that will contain the installed entry points during the installation, as the
build process needs them.
You may also need to install ``wheel`` first, if you have an older version of
pip and/or do not use virtualenv (which installs wheel by default).
Example::

 $ python -m pip install wheel --user
 $ PATH=$HOME/.local/bin:$PATH python -m pip install cppyy --user


PyPy
----

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


Precompiled Header
------------------

For performance reasons (reduced memory and CPU usage), a precompiled header
(PCH) of the system and compiler header files will be installed or, failing
that, generated on startup.
Obviously, this PCH is not portable and should not be part of any wheel.

Some compiler features, such as AVX, OpenMP, fast math, etc. need to be
active during compilation of the PCH, as they depend both on compiler flags
and system headers (for intrinsics, or API calls).
You can control compiler flags through the ``EXTRA_CLING_ARGS`` envar and thus
what is active in the PCH.
In principle, you can also change the C++ language standard by setting the
appropriate flag on ``EXTRA_CLING_ARGS`` and rebuilding the PCH.
However, if done at this stage, that disables some automatic conversion for
C++ types that were introduced after C++11 (such as string_view and optional).

If you want multiple PCHs living side-by-side, you can generate them
yourself (note that the given path must be absolute)::

 >>> import cppyy_backend.loader as l
 >>> l.set_cling_compile_options(True)         # adds defaults to EXTRA_CLING_ARGS
 >>> install_path = '/full/path/to/target/location/for/PCH'
 >>> l.ensure_precompiled_header(install_path)

You can then select the appropriate PCH with the ``CLING_STANDARD_PCH`` envar::

 $ export CLING_STANDARD_PCH=/full/path/to/target/location/for/PCH/allDict.cxx.pch

Or disable it completely by setting that envar to "none".


.. _`PyPI`: https://pypi.python.org/pypi/cppyy/
.. _`virtualenv`: https://pypi.python.org/pypi/virtualenv
.. _`through conda-forge`: https://anaconda.org/conda-forge/cppyy
.. _`Reflex`: https://root.cern.ch/how/how-use-reflex
