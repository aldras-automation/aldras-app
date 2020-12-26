import unittest
from modules.aldras_core import *


class TestInstance(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     print('setupClass')

    # @classmethod
    # def tearDownClass(cls):
    #     print('teardownClass')

    # def setUp(self):
    #     print('setUp')
    #     self.emp_1 = Employee('Corey', 'Schafer', 50000)
    #     self.emp_2 = Employee('Sue', 'Smith', 60000)

    # def tearDown(self):
    #     print('tearDown\n')

    def test_get_system_parameters(self):
        sys_params = get_system_parameters()

        for coord_num in [0, 1]:
            self.assertIsInstance(sys_params[coord_num], tuple,
                                  f'The return value of coordinate #{coord_num} should be a tuple.')

            for axis_dimenstion in [0, 1]:
                self.assertIsInstance(sys_params[coord_num][axis_dimenstion], int,
                                      f'The return value of coordinate #{coord_num} should be an integer.')

    def test_check_internet_connection(self):
        self.assertIsInstance(check_internet_connection(), bool)

    def test_coords_of(self):
        # testing different command diction
        self.assertEqual(coords_of('Left-mouse click at (742, 586)'), (742, 586))
        self.assertEqual(coords_of('Mouse-move to (536, 391)'), (536, 391))
        self.assertEqual(coords_of('Right-mouse press at (1118, 559)'), (1118, 559))
        self.assertEqual(coords_of('Right-mouse release at (1460, 810)'), (1460, 810))

        # testing different negative combinations
        self.assertEqual(coords_of('Left-mouse click at (-742, 810)'), (-742, 810))
        self.assertEqual(coords_of('Left-mouse click at (742, -810)'), (742, -810))
        self.assertEqual(coords_of('Left-mouse click at (-742, -810)'), (-742, -810))

        # testing zero coordinate filling
        self.assertEqual(coords_of('Left-mouse click at (, 810)'), (0, 810),
                         'Should be able to autofill zero coordinate.')
        self.assertEqual(coords_of('Left-mouse click at (742, )'), (742, 0),
                         'Should be able to autofill zero coordinate.')


if __name__ == '__main__':
    unittest.main()
