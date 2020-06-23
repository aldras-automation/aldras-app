"""Aldras module containing core functions used across classes"""
import re


def coords_of(line):
    """Returns tuple of parsed coordinates from string."""

    try:
        x_coord = re.findall(r'\d+', re.findall(r'(?<=\()(.*?)(?=,)', line)[0])[
            0]  # find first integer between '(' and','
    except IndexError:
        x_coord = 0
    try:
        y_coord = re.findall(r'\d+', re.findall(r'(?<=,)(.*?)(?=\))', line)[0])[
            0]  # find first integer between ',' and')'
    except IndexError:
        y_coord = 0

    return int(x_coord), int(y_coord)


def eliminate_duplicates(list_with_duplicates):
    """Eliminates duplicates from list"""
    seen = set()
    return [x for x in list_with_duplicates if not (x in seen or seen.add(x))]


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

