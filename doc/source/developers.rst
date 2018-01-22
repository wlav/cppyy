Developers
==========

Cppyy
-----

The ``cppyy`` module is a frontend (see :ref:`Package Structure
<package-structure>`), and most of the code is elsewhere. However, it does
contain the docs for all of the modules, which are built using
Sphinx: http://www.sphinx-doc.org/en/stable/ and published to
http://cppyy.readthedocs.io/en/latest/index.html using a webhook. To create
the docs::

    $ pip install sphinx_rtd_theme
    Collecting sphinx_rtd_theme
    ...
    Successfully installed sphinx-rtd-theme-0.2.4
    $ cd docs
    $ make html

The Python code in this module supports:

* Interfacing to the correct backend for CPython or PyPy.
* Pythonizations (TBD)

Cppyy-backend
-------------

The ``cppyy-backend`` module contains two areas:

* A patched copy of cling
* Wrapper code
