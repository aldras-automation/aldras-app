"""Aldras module containing core functions used across classes"""
import re


def float_in(input_string):
    """Returns parsed float from string."""
    floats = re.findall(r'[-+]?\d*\.\d+|\d+', input_string)
    if not floats:
        output = float(0)
    elif len(floats) > 1:
        output = [float(indiv_float) for indiv_float in floats]
    else:
        output = float(floats[0])

    return output


def variable_name_in(input_string):
    """Return variable in string between {{~ and ~}} syntax"""
    variables = re.findall(r'(?<={{~)(.*?)(?=~}})', input_string)
    if len(variables) == 1:
        return variables[0]
    else:
        raise ValueError


def assignment_variable_value_in(input_string):
    """Return string after equals sign"""
    return '='.join(input_string.split('=')[1:])


def conditional_operation_in(input_string, operations):
    """Return matching operation between ~}} and ~ syntax"""
    operation_in = re.search(r'(?<=~}})(.*?)(?=~)', input_string).group().lower()
    matching_operations_in = [element for element in operations if element.lower() in operation_in]
    if len(matching_operations_in) == 0:
        return ''
    return matching_operations_in[0]


def conditional_comparison_in(input_string):
    """Return matching operation between ~ and ~ syntax after variable {{~var~}}"""
    return re.search(r'(?<=~)(.*?)(?=~)', input_string.replace('{{~', '').replace('~}}', '')).group()

