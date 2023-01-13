import py, os, sys
from pytest import raises

currpath = py.path.local(__file__).dirpath()
test_dct = str(currpath.join("datatypesDict.so"))
test_h = str(currpath.join("datatypes.h"))

import cppyy

cppyy.load_library(test_dct)
cppyy.include(test_h)

gbl = cppyy.gbl

CppyyTestData = cppyy.gbl.CppyyTestData

c = CppyyTestData()
assert isinstance(c, CppyyTestData)

# test that the enum is accessible as a type
assert CppyyTestData.EWhat

assert CppyyTestData.kNothing   ==   6
assert CppyyTestData.kSomething == 111
assert CppyyTestData.kLots      ==  42

assert CppyyTestData.EWhat(CppyyTestData.kNothing) == CppyyTestData.kNothing
assert CppyyTestData.EWhat(6) == CppyyTestData.kNothing
# TODO: only allow instantiations with correct values (C++11)

assert c.get_enum() == CppyyTestData.kNothing
assert c.m_enum == CppyyTestData.kNothing

c.m_enum = CppyyTestData.kSomething
assert c.get_enum() == CppyyTestData.kSomething
assert c.m_enum == CppyyTestData.kSomething

c.set_enum(CppyyTestData.kLots)
assert c.get_enum() == CppyyTestData.kLots
assert c.m_enum == CppyyTestData.kLots

assert c.s_enum == CppyyTestData.s_enum
assert c.s_enum == CppyyTestData.kNothing
assert CppyyTestData.s_enum == CppyyTestData.kNothing

c.s_enum = CppyyTestData.kSomething
assert c.s_enum == CppyyTestData.s_enum
assert c.s_enum == CppyyTestData.kSomething
assert CppyyTestData.s_enum == CppyyTestData.kSomething

# global enums
assert gbl.EFruit          # test type accessible
assert gbl.kApple  == 78
assert gbl.kBanana == 29
assert gbl.kCitrus == 34
assert gbl.EFruit.__name__     == 'EFruit'
assert gbl.EFruit.__cpp_name__ == 'EFruit'

assert gbl.EFruit.kApple  == 78
assert gbl.EFruit.kBanana == 29
assert gbl.EFruit.kCitrus == 34

assert gbl.NamedClassEnum.E1 == 42
assert gbl.NamedClassEnum.__name__     == 'NamedClassEnum'
assert gbl.NamedClassEnum.__cpp_name__ == 'NamedClassEnum'

assert gbl.EnumSpace.E
assert gbl.EnumSpace.EnumClass.E1 == -1   # anonymous
assert gbl.EnumSpace.EnumClass.E2 == -1   # named type

assert gbl.EnumSpace.NamedClassEnum.E1 == -42
assert gbl.EnumSpace.NamedClassEnum.__name__     == 'NamedClassEnum'
assert gbl.EnumSpace.NamedClassEnum.__cpp_name__ == 'EnumSpace::NamedClassEnum'

raises(TypeError, setattr, gbl.EFruit, 'kBanana', 42)

assert gbl.g_enum == gbl.EFruit.kBanana
gbl.g_enum = gbl.EFruit.kCitrus
assert gbl.g_enum == gbl.EFruit.kCitrus

# typedef enum
assert gbl.EnumSpace.letter_code
assert gbl.EnumSpace.AA == 1
assert gbl.EnumSpace.BB == 2
