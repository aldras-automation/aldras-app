"""File to test loop execution ideas"""

with open('Workflows/Test_loop.txt', 'r') as record_file:
    lines_all = record_file.readlines()

lines_all = [line.strip('\n') for line in lines_all]


# print(lines_all)
#
# def execute_lines(index, lines):
#     global lines_all
#     for line in lines:
#         if 'loop' in line.lower() and '{' in line:
#             # execute_lines()
#             execute_lines(index, 3*[lines_all[index+1]])
#             pass
#         print(line)
#
# for index, line in enumerate(lines_all):
#     execute_lines(index, [line])

# get indices of loop block


def find_loop_lines(loop_start_index):
    indent_val = 0  # starting indent value of zero to be increased by the
    loop_end_index = -1  # return all lines after loop if no ending bracket is found in the loop below

    # loop through all lines starting from loop until ending bracket is found
    for loop_line_index, loop_line in enumerate(lines_all[loop_start_index:]):
        line_first_word = loop_line.strip().split(' ')[0].lower()

        if loop_line.strip() == '}':
            indent_val -= 1
        elif ('if' in line_first_word) and ('{' in loop_line):
            indent_val += 1
        elif ('loop' in line_first_word) and ('{' in loop_line):
            indent_val += 1

        if indent_val == 0:  # ending bracket is found
            loop_end_index = loop_start_index + loop_line_index
            break  # stop loop

    loop_lines = lines_all[loop_start_index + 1:loop_end_index]
    return loop_lines, loop_end_index


print(find_loop_lines(3))
