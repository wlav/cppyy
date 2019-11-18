.. _utilities:

Utilities
=========

The ``cppyy-backend`` package brings in the following utilities to help
with repackaging and redistribution:

  * cling-config: for compile time flags
  * rootcling and genreflex: for dictionary generation
  * cppyy-generator: part of the :doc:`CMake interface <cmake_interface>`


Compiler/linker flags
---------------------

``cling-config`` is a small utility to provide access to the as-installed
configuration, such as compiler/linker flags and installation directories, of
other components.
Usage examples::

    $ cling-config --help
    Usage: cling-config [--cflags] [--cppflags] [--cmake]
    $ cling-config --cmake
    /usr/local/lib/python2.7/dist-packages/cppyy_backend/cmake


.. _dictionaries:

Dictionaries
------------

Loading header files or code directly into ``cling`` is fine for interactive
work and smaller packages, but large scale applications benefit from
pre-compiling code, using the automatic class loader, and packaging
dependencies in so-called "dictionaries."

A `dictionary` is a generated C++ source file containing references to the
header locations used when building (and any additional locations provided),
a set of forward declarations to reduce the need of loading header files, and
a few I/O helper functions.
The name "dictionary" is historic: before ``cling`` was used, it contained
the complete generated C++ reflection information, whereas now that is
derived at run-time from the header files.
It is still possible to fully embed header files rather than only storing
their names and search locations, to make the dictionary more self-contained.

After generating the dictionary, it should be compiled into a shared library.
This provides additional dependency control: by linking it directly with any
further libraries needed, you can use standard mechanisms such as ``rpath``
to locate those library dependencies.
Alternatively, you can add the additional libraries to load to the mapping
files of the class loader (see below).

In tandem with any dictionary, a pre-compiled module (.pcm) file will be
generated.
C++ modules are still on track for inclusion in the C++20 standard and most
modern C++ compilers, ``clang`` among them, already have implementations.
The benefits for cppyy include faster bindings generation, lower memory
footprint, and isolation from preprocessor macros and compiler flags.
The use of modules is transparent, other than the requirement that they
need to be co-located with the compiled dictionary shared library.

Optionally, the dictionary generation process also produces a mapping file,
which lists the libraries needed to load C++ classes on request (for details,
see the section on the class loader below).


Generation
^^^^^^^^^^

There are two interfaces onto the dictionary generator: ``rootcling`` and
``genreflex``.
The reason for having two is historic and they are not complete duplicates,
so one or the other may suit your preference better.
It is foreseen that both will be replaced once C++ modules become more
mainstream, as that will allow simplification and improved robustness.

rootcling
"""""""""

This provides basic access to ``cling``::

    $ rootcling
    Usage: rootcling [-v][-v0-4] [-f] [out.cxx] [opts] file1.h[+][-][!] file2.h[+][-][!] ...[LinkDef.h]
    For more extensive help type: /usr/local/lib/python2.7/dist-packages/cppyy_backend/bin/rootcling -h

The basic mode of operation is to process the header files ('fileN.h')
according to certain `#pragmas in the LinkDef.h <https://root.cern.ch/root/html/guides/users-guide/AddingaClass.html#the-linkdef.h-file>`_
file in order to generate bindings accessible in Python under the 'cppyy.gbl'
namespace.

The output is

* A .cpp file (which, when compiled to a shared library)
* A .rootmap file
* A .pcm file

which are used at runtime by ``cling`` to expose the semantics expressed by the
header files to Python. Nominally, the compiled .cpp provides low-level Python
access to the library API defined by the header files, while ``cling`` uses the
other files to provide the rich features it supports. Thus, the shipping form
of the bindings contains:

* A shared library (which must be compiled from the .cpp)
* A .rootmap file
* A .pcm file

genreflex
"""""""""

The relevant headers are read by a tool called `genreflex`_ which generates
C++ files that are to be compiled into a shared library.
That library can further be linked with any relevant project libraries that
contain the implementation of the functionality declared in the headers.
For example, given a file called ``project_header.h`` and an implementation
residing in ``libproject.so``, the following will generate a
``libProjectDict.so`` reflection dictionary::

    $ genreflex project_header.h
    $ g++ -std=c++17 -fPIC -rdynamic -O2 -shared `genreflex --cppflags` project_header_rflx.cpp -o libProjectDict.so -L$PROJECTHOME/lib -lproject

Instead of loading the header text into Cling, you can now load the
dictionary:

.. code-block:: python

    >>> import cppyy
    >>> cppyy.load_reflection_info('libProjectDict.so')
    <CPPLibrary object at 0xb6fd7c4c>
    >>> from cppyy.gbl import SomeClassFromProject
    >>>

and use the C++ entities from the header as before.

.. _`genreflex`: https://linux.die.net/man/1/genreflex


.. _selection-files:

Sometimes it is necessary to restrict or expand what genreflex will pick up
from the header files.
For example, to add or remove standard classes or to hide implementation
details.
This is where `selection files`_ come in.
These are XML specifications that allow exact or pattern matching to classes,
functions, etc.
See ``genreflex --help`` for a detailed specification and add
``--selection=project_selection.xml`` to the ``genreflex`` command line.

With the aid of a selection file, a large project can be easily managed:
simply ``#include`` all relevant headers into a single header file that is
handed to ``genreflex``.

.. _`selection files`: https://linux.die.net/man/1/genreflex


Class loader
^^^^^^^^^^^^

Explicitly loading dictionaries is fine if this is hidden under the hood of
a Python package and thus simply done on import.
Otherwise, the automatic class loader is more convenient, as it allows direct
use without having to manually find and load dictionaries.

The class loader utilizes so-called rootmap files, which by convention should
live alongside the dictionaries in places reachable by LD_LIBRARY_PATH.
These are simple text files, which map C++ entities (such as classes) to the
dictionaries and other libraries that need to be loaded for their use.

The ``genreflex`` tool can produce rootmap files automatically.
For example::

    $ genreflex project_header.h --rootmap=libProjectDict.rootmap --rootmap-lib=libProjectDict.so
    $ g++ -std=c++17 -fPIC -rdynamic -O2 -shared `genreflex --cppflags` project_header_rflx.cpp -o libProjectDict.so -L$CPPYYHOME/lib -lCling -L$PROJECTHOME/lib -lproject

where the first option (``--rootmap``) specifies the output file name, and the
second option (``--rootmap-lib``) the name of the reflection library.
It is necessary to provide that name explicitly, since it is only in the
separate linking step where these names are fixed (if the second option is not
given, the library is assumed to be libproject_header.so).

With the rootmap file in place, the above example can be rerun without explicit
loading of the reflection info library:

.. code-block:: python

    >>> import cppyy
    >>> from cppyy.gbl import SomeClassFromProject
    >>>


.. _cppyy-generator:

Bindings collection
-------------------

``cppyy-generator`` is a clang-based utility program which takes a set of C++
header files and generates a JSON output file describing the objects found in
them.
This output is intended to support more convenient access to a set of
cppyy-supported bindings::

    $ cppyy-generator --help
    usage: cppyy-generator [-h] [-v] [--flags FLAGS] [--libclang LIBCLANG]
                           output sources [sources ...]
    ...

This utility is mainly used as part of the
:doc:`CMake interface <cmake_interface>`.
