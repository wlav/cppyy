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

        b = cppyy.gbl.Eigen.MatrixXd(2, 2)
        b[0,0] = 3
        assert b(0,0) == 3.
        b[1,0] = 2.5
        assert b(1,0) == 2.5
        b[0,1] = -1
        assert b(0,1) == -1.
        b[1,1] = b(1,0) + b(0,1)
        assert b(1,1) == b[1,0] + b[0,1]

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

        # equivalent of 'm << 12, 11, ..., 1' in C++
        c = (m << 12)
        for i in range(11, 0, -1):
            c = c.__comma__(i)
        assert m[0, 0] == 12.
        assert m[0, 1] == 11.
        assert m[0, 2] == 10.
        assert m[1, 0] ==  9.
        assert m[1, 1] ==  8.
        assert m[1, 2] ==  7.
        assert m[2, 0] ==  6.
        assert m[2, 1] ==  5.
        assert m[2, 2] ==  4.
        assert m[3, 0] ==  3.
        assert m[3, 1] ==  2.
        assert m[3, 2] ==  1.

        matA = cppyy.gbl.Eigen.MatrixXf(2, 2)
        (matA << 1).__comma__(2).__comma__(3).__comma__(4)
        matB = cppyy.gbl.Eigen.MatrixXf(4, 4)
        # TODO: the insertion operator is a template that expect only the base class
        #(matB << matA).__comma__(matA/10).__comma__(matA/10).__comma__(matA)

    def test03_matrices_and_vectors(self):
        """Matrices and vectors"""

        import cppyy

     # 'dynamic' matrices/vectors
        MatrixXd = cppyy.gbl.Eigen.MatrixXd
        VectorXd = cppyy.gbl.Eigen.VectorXd

        m = MatrixXd.Random(3, 3)
        assert m.rows() == 3
        assert m.cols() == 3
        m = (m + MatrixXd.Constant(3, 3, 1.2)) * 50

        v = VectorXd(3)
        (v << 1).__comma__(2).__comma__(3);

        assert (m*v).size() == v.size()

     # 'static' matrices/vectors
        Matrix3d = cppyy.gbl.Eigen.Matrix3d
        Vector3d = cppyy.gbl.Eigen.Vector3d

        m = Matrix3d.Random()
        m = (m + Matrix3d.Constant(1.2)) * 50

        v = Vector3d(1, 2, 3)

        assert (m*v).size() == v.size()
