import io
from pathlib import Path
import runpy
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import main


class CalculateTests(unittest.TestCase):
    def test_correct_expressions(self):
        examples = [
            ('3 0 4 ~ 2 ~', 47),
            ('2 2 + 4 - 4 ~ 2 3 * +', 22),
            ('8 3 -', 5),
            ('3 8 -', -5),
            ('8 2 /', 4),
            ('5 2 /', 2.5),
            ('-3 2 *', -6),
            ('1.5 2.25 +', 3.75),
            ('2 5 ~', 3),
            ('5 2 ~', 3),
            ('0 0 ~', 0),
            ('4 0 ~', 16),
            ('0 4 ~', 16),
            ('1 2 3 0 ~', 36),
            ('10 2 5 ~ +', 13),
            ('-3 0 2 ~', 1),
            ('42', 42),
            ('  2   3\t+  ', 5),
            ('0.1 0.2 +', 0.3),
        ]
        for expression, expected in examples:
            with self.subTest(expression=expression), redirect_stdout(io.StringIO()):
                self.assertAlmostEqual(main.calculate(expression), expected)

    def test_invalid_expressions(self):
        examples = [
            ('', 'пустое'), ('   ', 'пустое'),
            ('+', 'два числа'), ('2 ~', 'два числа'),
            ('2 0 /', 'делить на ноль'), ('2 -0 /', 'делить на ноль'),
            ('2 3', 'Не хватает операций'),
            ('2 abc +', 'не число'), ('2 3 ^', 'не число'),
            ('2,5 3 +', 'через точку'), ('2+3', 'пробелами'),
            ('nan', 'конечное'), ('inf', 'конечное'),
            ('1e999', 'конечное'),
            ('1e308 1e308 +', 'слишком большой'),
            ('1e200 0 ~', 'слишком большой'),
        ]
        for expression, message in examples:
            with self.subTest(expression=expression), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, message):
                    main.calculate(expression)

    def test_stack_after_every_step(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main.calculate('3 0 4 ~ 2 ~')
        self.assertEqual(output.getvalue().splitlines(), [
            'Шаг 1: 3 -> [3]',
            'Шаг 2: 0 -> [3, 0]',
            'Шаг 3: 4 -> [3, 0, 4]',
            'Шаг 4: ~ -> [49]',
            'Шаг 5: 2 -> [49, 2]',
            'Шаг 6: ~ -> [47]',
        ])


class CommandLineTests(unittest.TestCase):
    def run_program(self, arguments):
        output = io.StringIO()
        errors = io.StringIO()
        # patch.object (объект у которого заменяем, какой атрибут заменяем, новое значение)
        with patch.object(sys, 'argv', ['main.py'] + arguments):
            with redirect_stdout(output), redirect_stderr(errors):
                with self.assertRaises(SystemExit) as exit_info:
                    runpy.run_path(str(Path(__file__).with_name('main.py')), run_name='__main__')
        return exit_info.exception.code, output.getvalue(), errors.getvalue()

    def test_success(self):
        for arguments in [['5 2 /'], ['5', '2', '/']]:
            with self.subTest(arguments=arguments):
                code, output, errors = self.run_program(arguments)
                self.assertEqual(code, 0)
                self.assertTrue(output.endswith('5 2 / = 2.5\n'))
                self.assertEqual(errors, '')

    def test_error(self):
        code, output, errors = self.run_program(['1 0 /'])
        self.assertEqual(code, 1)
        self.assertIn('делить на ноль', errors)
        self.assertNotIn(' = ', output)
        self.assertNotIn('Traceback', errors)

    def test_help_and_missing_arguments(self):
        for arguments, expected in [([], 1), (['-h'], 0), (['--help'], 0)]:
            with self.subTest(arguments=arguments):
                code, output, errors = self.run_program(arguments)
                self.assertEqual(code, expected)
                self.assertIn('Использование:', output)
                self.assertEqual(errors, '')


if __name__ == '__main__':
    unittest.main()
