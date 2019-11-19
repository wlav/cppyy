import py, os, sys
from pytest import mark, raises
from .support import setup_make

inc_paths = [os.path.join(os.path.sep, 'usr', 'include'),
             os.path.join(os.path.sep, 'usr', 'local', 'include')]

eigen_path = None
for p in inc_paths:
    p = os.path.join(p, 'eigen3')
    if os.path.exists(p):
        eigen_path = p


@mark.skipif(eigen_path is None, reason="Eigen not found")
class TestEIGEN:
    def setup_class(cls):
        import cppyy

        cppyy.add_include_path(eigen_path)
        cppyy.include('Eigen/Dense')

    def test01_simple_matrix(self):
        """Basic creation of an Eigen::Matrix"""

        import cppyy

        a = cppyy.gbl.Eigen.Matrix['double', 2, 2]()
        assert a.rows() == 2
        assert a.cols() == 2

    def test02_comma_insertion(self):
        """Comma insertion overload"""

        import cppyy

        m = cppyy.gbl.Eigen.MatrixXd(2, 5)
        assert m.rows() == 2
        assert m.cols() == 5

        # TODO: this calls a conversion to int ...
        #m.resize(cppyy.gbl.Eigen.NoChange_t(), 3)
        #assert m.rows() == 2
        #assert m.cols() == 3

        m.resize(4, 3)
        assert m.rows() == 4
        assert m.cols() == 3
