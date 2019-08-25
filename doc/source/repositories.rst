.. _repositories:

Repositories
============

The ``cppyy`` module is a frontend that requires an intermediate (Python
interpreter dependent) layer, and a backend (see
:ref:`Package Structure <package-structure>`).
Because of this layering and because it leverages several existing packages
through reuse, the relevant codes are contained across a number of
repositories.

* Frontend, cppyy: https://bitbucket.org/wlav/cppyy
* CPython (v2/v3) intermediate: https://bitbucket.org/wlav/cpycppyy
* PyPy intermediate (module _cppyy): https://bitbucket.org/pypy/pypy/
* Backend, cppyy: https://bitbucket.org/wlav/cppyy-backend

The backend repo contains both the cppyy-cling (under "cling") and
cppyy-backend (under "clingwrapper") packages.


Building
--------

Except for cppyy-cling, the structure in the repositories follows a normal
PyPA package and they are thus ready to build with `setuptools`_: simply
clone the package and either run ``python setup.py``, or use ``pip``.

It is highly recommended to follow the dependency chain when manually
upgrading packages individually (i.e. cppyy-cling, cppyy-backend, CPyCppyy
if on CPython, and then finally cppyy), because upstream packages expose
headers that are used by the ones downstream.
Of course, if only building for a patch/point release, there is no need to
re-install the full chain (or follow the order).
Always run the local updates from the package directories (i.e. where the
``setup.py`` file is located), as some tools rely on the package structure.

Start with the ``cppyy-cling`` package (cppyy-backend repo, subdirectory
"cling"), which requires source to be pulled in from upstream, and thus takes
a few extra steps::

 $ git clone https://bitbucket.org/wlav/cppyy-backend.git
 $ cd cppyy-backend/cling
 $ python setup.py egg_info
 $ python create_src_directory.py
 $ python -m pip install . --upgrade

The ``egg_info`` setup command is needed for ``create_src_directory.py`` to
find the right version.
It in turn downloads the proper release from upstream, trims and patches it,
and installs the result in the "src" directory.
When done, the structure of ``cppyy-cling`` looks again like a PyPA package
and can be used/installed as expected, here using ``pip``.

Next, ``cppyy-backend`` (cppyy-backend, subdirectory "clingwrapper"; omit the
first step if you already cloned the repo for ``cppyy-cling``)::

 $ git clone https://bitbucket.org/wlav/cppyy-backend.git
 $ cd cppyy-backend/clingwrapper
 $ python -m pip install . --upgrade

Upgrading ``CPyCppyy`` and ``cppyy`` is very similar.
First, ``CPyCppyy``::

 $ git clone https://bitbucket.org/wlav/CPyCppyy.git
 $ cd CPyCppyy
 $ python -m pip install . --upgrade

Then ``cppyy``::

 $ git clone https://bitbucket.org/wlav/cppyy.git
 $ cd cppyy
 $ python -m pip install . --upgrade

Please see the `pip documentation`_ for more options, such as developer mode; and
the :ref:`installation section <intallation_from_source>`, for more installation
options, such as selectin the desired C++ standard.

.. _`setuptools`: https://setuptools.readthedocs.io/
.. _`pip documentation`: https://pip.pypa.io/
