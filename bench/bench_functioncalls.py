import py, pytest, os, sys, math, warnings
from support import setup_make


setup_make("functioncallsDict.so")

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("functioncallsDict.so"))

import cppyy
cppyy.load_reflection_info(test_dct)

import py_functioncalls

bench_strings = [('py', 'py_functioncalls'), ('cppyy', 'cppyy.gbl')]

N = 10000

try:
    import py11_functioncalls
    bench_strings.append(('py11', 'py11_functioncalls'))
    py11 = True
except ImportError:
    warnings.warn('pybind11 tests disabled')
    py11 = False

try:
    import swig_functioncalls
    bench_strings.append(('swig', 'swig_functioncalls'))
    swig = True
except ImportError:
    warnings.warn('swig tests disabled')
    swig = False

if sys.hexversion < 0x3000000:
    looprange = xrange
else:
    looprange = range


#- group: empty-free ---------------------------------------------------------
group = 'empty-free'

def call_instance_empty(inst):
    for i in looprange(N):
        inst.empty_call()

benches = """
@pytest.mark.benchmark(group=group, warmup=True)
def test_{0}_free_empty_call(benchmark):
    benchmark({1}.empty_call)
"""

for label, modname in bench_strings:
    exec(benches.format(label, modname))


#- group: empty-inst ---------------------------------------------------------
group = 'empty-inst'

def call_instance_empty(inst):
    for i in looprange(N):
        inst.empty_call()

benches = """
{0}_inst_empty = {1}.EmptyCall()
@pytest.mark.benchmark(group=group, warmup=True)
def test_{0}_inst_empty_call(benchmark):
    benchmark(call_instance_empty, {0}_inst_empty)
"""

for label, modname in bench_strings:
    exec(benches.format(label, modname))


#- group: builtin-args -------------------------------------------------------
def py_take_a_value(val):
    pass

group = 'free-builtin-args'
@pytest.mark.benchmark(group=group, warmup=True)
def test_py_take_a_value(benchmark):
    benchmark(py_take_a_value, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_take_an_int(benchmark):
    benchmark(cppyy.gbl.take_an_int, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_take_a_double(benchmark):
    benchmark(cppyy.gbl.take_a_double, 1.)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_take_a_value(benchmark):
    benchmark(cppyy.gbl.take_a_value, cppyy.gbl.Value())


group = 'inst-builtin-args'
inst2 = cppyy.gbl.TakeAValue()
@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_take_an_int(benchmark):
    benchmark(inst2.take_an_int, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_take_a_double(benchmark):
    benchmark(inst2.take_a_double, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_take_a_value(benchmark):
    benchmark(inst2.take_a_value, cppyy.gbl.Value())


if py11:
    py11_inst2 = py11_functioncalls.TakeAValue()
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_py11_inst_take_an_int(benchmark):
        benchmark(py11_inst2.take_an_int, 1)

    @pytest.mark.benchmark(group=group, warmup=True)
    def test_py11_inst_take_a_double(benchmark):
        benchmark(py11_inst2.take_a_double, 1)

    @pytest.mark.benchmark(group=group, warmup=True)
    def test_py11_inst_take_a_value(benchmark):
        benchmark(py11_inst2.take_a_value, py11_functioncalls.Value())


if swig:
    swig_inst2 = swig_functioncalls.TakeAValue()
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_swig_inst_take_an_int(benchmark):
        benchmark(swig_inst2.take_an_int, 1)

    @pytest.mark.benchmark(group=group, warmup=True)
    def test_swig_inst_take_a_double(benchmark):
        benchmark(swig_inst2.take_a_double, 1)

    @pytest.mark.benchmark(group=group, warmup=True)
    def test_swig_inst_take_a_value(benchmark):
        benchmark(swig_inst2.take_a_value, swig_functioncalls.Value())


#- group: do-work ------------------------------------------------------------
def py_do_work(val):
    return math.atan(val)

group = 'do-work'
@pytest.mark.benchmark(group=group, warmup=True)
def test_py_do_work(benchmark):
    benchmark(py_do_work, 1.)

@pytest.mark.benchmark(group=group, warmup=True)
def test_cppyy_free_do_work(benchmark):
    benchmark(cppyy.gbl.do_work, 1.)

cppyy_inst3 = cppyy.gbl.DoWork()
@pytest.mark.benchmark(group=group, warmup=True)
def test_cppyy_inst_do_work(benchmark):
    benchmark(cppyy_inst3.do_work, 1.)


"""if py11:
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_py11_free_do_work(benchmark):
        benchmark(py11_functioncalls.do_work, 1.)

    py11_inst3 = py11_functioncalls.DoWork()
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_py11_inst_do_work(benchmark):
        benchmark(py11_inst3.do_work, 1.)"""


if swig:
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_swig_free_do_work(benchmark):
        benchmark(swig_functioncalls.do_work, 1.)

    swig_inst3 = swig_functioncalls.DoWork()
    @pytest.mark.benchmark(group=group, warmup=True)
    def test_swig_inst_do_work(benchmark):
        benchmark(swig_inst3.do_work, 1.)
