import unittest
from elliptic import add_points, calculate_table_inv, mul, add, calculate_double, calculate_table_sqrt, calculate_base_point, calculate_curve_y, is_on_curve, calculate_fast_mul_point, calculate_fast_mul_table

class TestEllipticCurveFunction(unittest.TestCase):

    def test_calculate_table_inv(self):
        table_inv = calculate_table_inv()
        for key, value in table_inv.items():
            self.assertEqual(mul(key, value), 1)

    def test_calculate_base_point(self):
        table_sqrt = calculate_table_sqrt()
        base_point = calculate_base_point(table_sqrt)
        self.assertTrue(is_on_curve(base_point), 'Base point is not on the curve')

    def test_add_points_on_curve(self):
        table_inv = calculate_table_inv()
        table_sqrt = calculate_table_sqrt()
        point1 = calculate_base_point(table_sqrt)
        x = point1[0] - 2 # tweak this until you find some point on the curve
        point2 = (x, calculate_curve_y(x, 0, table_sqrt))

        assert is_on_curve(point1)
        assert is_on_curve(point2)

        point = add_points(point1, point2, table_inv)
        print(point1, point2, point)

        self.assertTrue(is_on_curve(point), 'Double point is not on the curve {}'.format(point))

    def test_calculate_double_on_curve(self):
        table_inv = calculate_table_inv()
        table_sqrt = calculate_table_sqrt()
        base_point = calculate_base_point(table_sqrt)
        point = calculate_double(base_point, table_inv)
        self.assertTrue(is_on_curve(point), 'Double point is not on the curve {}'.format(point))

    def test_add_points(self):
        table_inv = calculate_table_inv()
        table_sqrt = calculate_table_sqrt()
        point1 = calculate_base_point(table_sqrt)
        point2 = calculate_double(point1, table_inv)
        point4 = calculate_double(point2, table_inv)
        point8 = calculate_double(point4, table_inv)
        self.assertEqual(
            add_points(point1, point4, table_inv), 
            add_points(point4, point1, table_inv))
        self.assertEqual(
            add_points(point1, point8, table_inv), # 1 + 8
            add_points(add_points(point4, point4, table_inv), point1, table_inv) # 4 + 4 + 1
        )

    def test_calculate_fast_mul_point(self):
        table_inv = calculate_table_inv()
        table_sqrt = calculate_table_sqrt()
        point1 = calculate_base_point(table_sqrt)
        point2 = calculate_double(point1, table_inv)
        point4 = calculate_double(point2, table_inv)
        point8 = calculate_double(point4, table_inv)

        # Make sure the result is on the curve
        self.assertTrue(is_on_curve(calculate_fast_mul_point(1, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(3, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(5, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(7, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(8, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(15, point1, table_inv)))
        self.assertTrue(is_on_curve(calculate_fast_mul_point(60, point1, table_inv)))

        # Make sure we end up in the same place adding the points manually and using fast multiplication
        self.assertEqual(
            calculate_fast_mul_point(1, point1, table_inv), 
            point1
        )
        self.assertEqual(
            calculate_fast_mul_point(15, point1, table_inv), 
            add_points(add_points(add_points(point4, point1, table_inv), point2, table_inv), point8, table_inv)
        )
        self.assertEqual(
            calculate_fast_mul_point(14, point1, table_inv), 
            add_points(add_points(point2, point4, table_inv), point8, table_inv)
        )

        # Make sure is commutative
        self.assertEqual(
            calculate_fast_mul_point(1, calculate_fast_mul_point(2, point1, table_inv), table_inv),
            calculate_fast_mul_point(2, calculate_fast_mul_point(1, point1, table_inv), table_inv),            
        )
        

if __name__ == '__main__':
    unittest.main()