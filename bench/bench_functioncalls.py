import py, pytest, os, sys, math
from support import setup_make


setup_make("functioncallsDict.so")

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("functioncallsDict.so"))

import cppyy
cppyy.load_reflection_info(test_dct)


#- group: empty --------------------------------------------------------------
def py_empty_call():
    pass

group = 'empty'
@pytest.mark.benchmark(group=group, warmup=True)
def test_py_empty_call(benchmark):
    benchmark(py_empty_call)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_empty_call(benchmark):
    benchmark(cppyy.gbl.empty_call)

inst1 = cppyy.gbl.EmptyCall()
@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_empty_call(benchmark):
    benchmark(inst1.empty_call)


#- group: builtin-args -------------------------------------------------------
def py_take_a_value(val):
    pass

group = 'builtin-args'
@pytest.mark.benchmark(group=group, warmup=True)
def test_py_take_a_value(benchmark):
    benchmark(py_take_a_value, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_take_an_int(benchmark):
    benchmark(cppyy.gbl.take_an_int, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_take_a_double(benchmark):
    benchmark(cppyy.gbl.take_a_double, 1.)

inst2 = cppyy.gbl.TakeAValue()
@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_take_an_int(benchmark):
    benchmark(inst2.take_an_int, 1)

@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_take_a_double(benchmark):
    benchmark(inst2.take_a_double, 1)


#- group: do-work ------------------------------------------------------------
def py_do_work(val):
    return math.atan(val)

group = 'do-work'
@pytest.mark.benchmark(group=group, warmup=True)
def test_py_do_work(benchmark):
    benchmark(py_do_work, 1.)

@pytest.mark.benchmark(group=group, warmup=True)
def test_free_do_work(benchmark):
    benchmark(cppyy.gbl.do_work, 1.)

inst3 = cppyy.gbl.DoWork()
@pytest.mark.benchmark(group=group, warmup=True)
def test_inst_do_work(benchmark):
    benchmark(inst3.do_work, 1.)

