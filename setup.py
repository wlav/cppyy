#!/usr/bin/env python

import codecs, glob, os, sys, re
from distutils import log
from setuptools import setup, find_packages, Extension
from setuptools.command.install import install as _install
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    has_wheel = True
except ImportError:
    has_wheel = False


here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

_is_manylinux = None
def is_manylinux():
    global _is_manylinux
    if _is_manylinux is None:
        _is_manylinux = False
        try:
            for line in open('/etc/redhat-release').readlines():
                if 'CentOS release 5.11' in line:
                    _is_manylinux = True
                    break
        except (OSError, IOError):
            pass
    return _is_manylinux

add_pkg = ['cppyy']
try:
    import __pypy__, sys
    version = sys.pypy_version_info
    requirements = ['cppyy-backend']
    if version[0] == 5:
        if version[1] <= 9:
            requirements = ['cppyy-cling<6.12', 'cppyy-backend<0.3']
            add_pkg += ['cppyy_compat']
        elif version[1] <= 10:
            requirements = ['cppyy-cling', 'cppyy-backend<0.4']
    elif version[0] == 6:
        if version[1] <= 0:
            requirements = ['cppyy-cling', 'cppyy-backend<1.1']
except ImportError:
    # CPython
    requirements = ['CPyCppyy>=1.4.0']

setup_requirements = ['wheel']
if not 'egg_info' in sys.argv:
    setup_requirements += requirements

# https://packaging.python.org/guides/single-sourcing-package-version/
def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

class my_install(_install):
    def run(self):
        # base install
        _install.run(self)

        if 'linux' in sys.platform:
            # force build of the .pch underneath the cppyy package, so that
            # it will be removed on upgrade/uninstall
            install_path = os.path.join(os.getcwd(), self.install_libbase, 'cppyy')

            try:
                import cppyy_backend.loader as l
                log.info("installing pre-compiled header in %s", install_path)
                l.set_cling_compile_options(True)
                l.ensure_precompiled_header(install_path)
            except (ImportError, AttributeError):
                # ImportError may occur with wrong pip requirements resolution (unlikely)
                # AttributeError will occur with (older) PyPy as it relies on older backends
                pass

cmdclass = {
        'install': my_install }
if has_wheel:
    class my_bdist_wheel(_bdist_wheel):
        def run(self, *args):
         # wheels do not respect dependencies; make this a no-op, unless it is
         # explicit building for manylinux
            if is_manylinux():
                print('###################### WHEELIE!')
                return _bdist_wheel.run(self, *args)
    cmdclass['bdist_wheel'] = my_bdist_wheel

# same for bdist_egg as for bdist_wheel (see above)
class my_bdist_egg(_bdist_egg):
    def run(self, *args):
        if is_manylinux():
            return _bdist_egg.run(self, *args)
cmdclass['bdist_egg'] = my_bdist_egg


setup(
    name='cppyy',
    version=find_version('python', 'cppyy', '_version.py'),
    description='Cling-based Python-C++ bindings',
    long_description=long_description,

    url='http://cppyy.readthedocs.org',

    # Author details
    author='Wim Lavrijsen',
    author_email='WLavrijsen@lbl.gov',

    license='LBNL BSD',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Software Development',
        'Topic :: Software Development :: Interpreters',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: C',
        'Programming Language :: C++',

        'Natural Language :: English'
    ],

    setup_requires=setup_requirements,
    install_requires=requirements,

    keywords='C++ bindings data science calling language integration',

    package_dir={'': 'python'},
    packages=find_packages('python', include=add_pkg),

    cmdclass = cmdclass,
)
