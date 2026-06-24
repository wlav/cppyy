import hypothesis
from hypothesis import given, settings, example, note, strategies as st
import cppyy
import pytest

cppyy.cppdef("""
    namespace test {
    template <typename T>
    constexpr std::size_t tuple_size(const T&) {
        return std::tuple_size<T>::value;
    }

    constexpr bool as_bool(auto b) {
        return static_cast<bool>(b);
    }

    template<typename... Ts>
    struct list {
        template<typename... Us>
        constexpr auto operator==(list<Us...>) const -> bool {
            return false;
        }

        constexpr auto operator==(list<Ts...>) const -> bool {
            return true;
        }
    };

    template<typename... Ts>
    constexpr auto make_list(Ts...) {
        return list<Ts...>{};
    }

    template<typename... Ls, typename... Rs>
    constexpr auto cat(list<Ls...>, list<Rs...>) {
        return list<Ls..., Rs...>{};
    }
    } // namespace test
""")

class TestRandomTemplates:
    bools = st.booleans().map(lambda v: cppyy.gbl.test.as_bool(v))

    def make_c_type_strat(t):
        min_val = cppyy.gbl.std.numeric_limits[t].min()
        max_val = cppyy.gbl.std.numeric_limits[t].max()
        return st.integers(min_value=int(min_val), max_value=int(max_val)).map(lambda v: t(v))

    int16s = make_c_type_strat(cppyy.gbl.std.int16_t)
    int32s = make_c_type_strat(cppyy.gbl.std.int32_t)
    int64s = make_c_type_strat(cppyy.gbl.std.int64_t)

    uint16s = make_c_type_strat(cppyy.gbl.std.uint16_t)
    uint32s = make_c_type_strat(cppyy.gbl.std.uint32_t)
    uint64s = make_c_type_strat(cppyy.gbl.std.uint64_t)

    cpp_primitives = st.one_of(bools, int16s, int32s, int64s, uint16s, uint32s, uint64s)

    @classmethod
    def as_std_tuple_tree(cls, value):
        if isinstance(value, list):
            values = [cls.as_std_tuple_tree(v) for v in value]
            return std.make_tuple(*values)
        else:
            return value

    @classmethod
    def as_test_list_tree(cls, value):
        if isinstance(value, list):
            values = [cls.as_test_list_tree(v) for v in value]
            return cppyy.gbl.test.make_list[tuple(type(v) for v in values)](*values)
        else:
            return value

    @st.composite
    def py_list_trees(draw, leaves=cpp_primitives):
        t = draw(st.recursive(leaves, lambda children: st.lists(children)))
        
        if not isinstance(t, list):
            t = [t]

        return t

    # TODO: uncomment once #261 is fixed
    # @given(st.lists(cpp_primitives))
    # def test_std_tuple_size(pytestconfig, ints):
    #     assert cppyy.gbl.test.tuple_size(cppyy.gbl.std.make_tuple(*ints)) == len(ints)

    # TODO: uncomment once #261 is fixed
    # @classmethod
    # @settings(deadline=2000)
    # @given(py_list_trees(), py_list_trees())
    # @example([0], [[], []])
    # def test_std_tuple_cat(cls, pytestconfig, left, right):
    #     expected = cls.as_std_tuple_tree(left + right)
    #     actual = cppyy.gbl.std.tuple_cat(cls.as_std_tuple_tree(left), cls.as_std_tuple_tree(right))
    #     assert actual == expected

    @classmethod
    @settings(deadline=2000)
    @given(py_list_trees(), py_list_trees())
    @example([0], [[], []])
    def test_list_cat(cls, pytestconfig, left, right):
        expected = cls.as_test_list_tree(left + right)
        actual = cppyy.gbl.test.cat(cls.as_test_list_tree(left), cls.as_test_list_tree(right))
        assert actual == expected
