"""Вычисление выражения в постфиксной нотации с помощью списка-стека"""

import math
import sys


def format_number(number):
    """У целого результата убираем ненужную дробную часть"""
    if number.is_integer():
        return str(int(number))
    return str(number)


def calculate(expression):
    tokens = expression.split()
    if not tokens:
        raise ValueError('Выражение пустое')

    stack = []
    for step, token in enumerate(tokens, start=1):
        if token in ('+', '-', '*', '/', '~'):
            if len(stack) < 2:
                raise ValueError(
                    f'Шаг {step}: для операции "{token}" нужны два числа.'
                )

            # В постфиксной записи первым снимается правый операнд
            y = stack.pop()
            x = stack.pop()
            if token == '+':
                result = x + y
            elif token == '-':
                result = x - y
            elif token == '*':
                result = x * y
            elif token == '/':
                if y == 0:
                    raise ValueError(f'Шаг {step}: делить на ноль нельзя')
                result = x / y
            elif x != 0 and y != 0:
                result = abs(x - y)
            else:
                # Суммируем весь стек вместе со снятыми числами
                total = sum(stack) + x + y
                result = total * total
                stack.clear()

            if not math.isfinite(result):
                raise ValueError(f'Шаг {step}: результат слишком большой')
            stack.append(result)
        else:
            try:
                number = float(token)
            except ValueError:
                raise ValueError(
                    f'Шаг {step}: "{token}" — не число и не операция\n'
                    'Разделяйте числа и операции пробелами; дроби пишите через точку'
                ) from None
            if not math.isfinite(number):
                raise ValueError(f'Шаг {step}: нужно конечное число, получено "{token}"')
            stack.append(number)

        state = ', '.join(format_number(number) for number in stack)
        print(f'Шаг {step}: {token} -> [{state}]')

    if len(stack) != 1:
        raise ValueError(
            f'В стеке осталось чисел: {len(stack)}. Не хватает операций'
        )
    return stack[0]


def main():
    if len(sys.argv) == 1 or sys.argv[1:] in (['-h'], ['--help']):
        print('Использование: python main.py "2 3 +"')
        print('Операции: + - * / ~. Разделяйте элементы пробелами')
        print('Заключайте выражение в кавычки, чтобы оболочка не изменяла * и ~')
        return 0 if len(sys.argv) > 1 else 1

    expression = ' '.join(sys.argv[1:])
    try:
        result = calculate(expression)
    except ValueError as error:
        print(f'Ошибка: {error}', file=sys.stderr)
        return 1

    print(f'{expression} = {format_number(result)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
