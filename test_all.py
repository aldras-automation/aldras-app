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

    def test_eliminate_duplicates(self):
        self.assertEqual(eliminate_duplicates(['V', 'Ctrl', 'V']), ['V', 'Ctrl'])
        self.assertEqual(eliminate_duplicates(['a', 'b', 'a', 'c', 'c']), ['a', 'b', 'c'])

    def test_float_in(self):
        self.assertEqual(float_in('Wait 0.5'), 0.5)
        self.assertEqual(float_in('Float one is 4.512351, float two is 0, float three is 8', True),
                         [4.512351, 0.0, 8.0])

    def test_variable_names_in(self):
        self.assertEqual(variable_names_in('Variable test string {{~var.1~}} - {{~var.2~}} and {{~var.3~}}'),
                         ['var.1', 'var.2', 'var.3'])
        self.assertEqual(variable_names_in('Single variable test string {{~var.1~}}'), ['var.1'])
        self.assertEqual(variable_names_in('Special characters variable test string {{~{var~1}~}}'), ['{var~1}'])

    def test_assignment_variable_value_in(self):
        self.assertEqual(assignment_variable_value_in('Assign {{~var1~}}=Test value'), 'Test value')
        self.assertEqual(assignment_variable_value_in('Assign {{~equation~}}=It is x=y'), 'It is x=y')

    def test_conditional_operation_in(self):
        conditional_operations = ['Equals', 'Not equal to', 'Contains', 'Is in', '>', '<', '>=', '<=']
        self.assertEqual(conditional_operation_in('If {{~Var~}} equals ~value~ {', conditional_operations), 'Equals')
        self.assertEqual(conditional_operation_in('If {{~Var~}} >= ~value~ {', conditional_operations), '>=')

    def test_conditional_comparison_in(self):
        self.assertEqual(conditional_comparison_in('If {{~Var~}} >= ~value~ {'), 'value')

    def test_loop_table_data_from(self):
        self.assertEqual(
            loop_table_data_from("Loop for each row in table [1`'`2`'`3`'''`A`'`B`'`C`'''`AA`'`BB`'`CC] {"),
            (["1`'`2`'`3", "A`'`B`'`C", "AA`'`BB`'`CC"], ['1', '2', '3']))

    def test_block_end_index(self):
        self.assertEqual(block_end_index(['Type:Stuff',
                                          "Loop for each row in table [Name`'`ID`'`Country`'''`John Smith`'`1111`'`UK`'''`Amy Baker`'`2222`'`US] {",
                                          'Left-mouse click at (10, 10)', 'Hotkey Ctrl + C', 'Type:', '}',
                                          'Left-mouse click at (10, 10)', 'Left-mouse click at (10, 10)'], 1), 5)
        self.assertEqual(block_end_index(['Type:Stuff',
                                          "Loop for each row in table [Name`'`ID`'`Country`'''`John Smith`'`1111`'`UK`'''`Amy Baker`'`2222`'`US] {",
                                          'Left-mouse click at (10, 10)', 'Hotkey Ctrl + C', 'Type:',
                                          'Left-mouse click at (10, 10)', 'Left-mouse click at (10, 10)'], 1), -1)


if __name__ == '__main__':
    unittest.main()
