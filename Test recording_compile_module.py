def coords_of(line):
    """Returns tuple of parsed coordinates from string."""
    coords = line.split('(')[1].replace(' ', '').replace(')', '').split(',')
    try:
        x_coord = int(coords[0])
    except ValueError:
        x_coord = 0

    try:
        y_coord = int(coords[1])
    except ValueError:
        y_coord = 0

    coords = (x_coord, y_coord)
    return coords


def eliminate_duplicates(list_with_duplicates):
    """Function eliminate duplicates from list"""
    seen = set()
    seen_add = seen.add
    return [x for x in list_with_duplicates if not (x in seen or seen_add(x))]


def consecutive_ranges_of(list_in):
    nums = sorted(set(list_in))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s + 1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))


recording_lines = ['Key ctrl_l press at (955, 581)', 'Key t press', 'Key t release', 'Key ctrl_l release at (955, 581)',
                   'Key shift press', 'Key t press', 'Key shift release', 'Key t release', 'Key h press',
                   'Key h release', 'Key i press', 'Key i release', 'Key s press', 'Key s release', 'Key space press',
                   'Key space release', 'Key i press', 'Key i release', 'Key s press', 'Key s release',
                   'Key space press', 'Key space release', 'Key a press', 'Key a release', 'Key space press',
                   'Key space release', 'Key t press', 'Key t release', 'Key e press', 'Key e release', 'Key s press',
                   'Key t press', 'Key s release', 'Key t release', 'Key . press', 'Key . release', 'Key space press',
                   'Key space release', 'Key space press', 'Key space release', 'Key space press', 'Key space release',
                   'Key backspace press', 'Key backspace release', 'Key backspace press', 'Key backspace release',
                   'Key backspace press', 'Key backspace release']

recording_lines = ['Key shift press', 'Key y press', 'Key y release', 'Key shift release', 'Key o press',
                   'Key o release', 'Key shift_r press', 'Key ! press', 'Key ! release', 'Key shift_r release']

###################################################################################################################
###################################################################################################################

# global recording_lines
lines = recording_lines
print('lines: {}'.format(lines))

mouse_hover_duration = 0.5
processed_lines = []
skip = False
break_code = '```8729164788```'
break_value = ''
register_hotkey = False
pressed_keys = []
symbol_chars = ['[', '@', '_', '!', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{',
                '~', ':', ']']
replacement_keys_ref = {
    'ctrl': ['ctrl_l', 'ctrl_r'],
    'alt': ['alt_gr', 'alt_l', 'alt_r'],
    'shift': ['shift_l', 'shift_r'],
    'cmd': ['cmd_l', 'cmd_r'],
}
for index, line in enumerate(lines[:-1]):  # loop through all lines except last one (should be release)
    if not skip:
        line = line.replace('shift_l', 'shift').replace('shift_r', 'shift')
        print('line: {}'.format(line))
        key = line.split(' ')[1]
        print('key: {}'.format(key))

        if not pressed_keys and lines[index].replace('press', '') == lines[index + 1].replace('release',
                                                                                              ''):  # if line press is same as next line release
            print('ONLY TAP')

            skip = True  # skip the next (release) line
            if len(key) > 1:  # special functions

                if 'ctrl_l' in line:  # if left ctrl is in line signalling mouse-move
                    coords = coords_of(line)
                    line = 'Mouse-move to {}{}Wait {}{}'.format((coords[0], coords[1]), break_code,
                                                                mouse_hover_duration, break_code)

                elif key == 'space':
                    line = 'Type: '

                else:
                    if 'mouse' in line:
                        tap_replacement = 'click'
                    else:
                        tap_replacement = 'tap'
                    line = lines[index].replace('press', tap_replacement)

                processed_line = break_code + line + break_code

            else:  # alphanumeric keys (try to compile into type command)
                processed_line = break_code + 'Type:{}'.format(key) + break_code

        else:  # line press not equal to next line release
            print('NOT TAP: {}'.format(line))
            if 'Key' in line:
                if 'press' in line:
                    if index != len(lines) - 1:
                        pressed_keys.append(key)
                        pressed_keys = eliminate_duplicates(pressed_keys)
                        register_hotkey = True
                        line = ''

                if 'release' in line and key in pressed_keys:
                    # execute hotkey
                    if register_hotkey:
                        check_single_chars = {len(x) for x in pressed_keys if x != 'shift'} == {
                            1}  # all hotkeys are single chars
                        check_alphabet_letters = {x.isalpha() for x in pressed_keys if x != 'shift'} == {
                            True}  # all hotkeys are alphabet
                        check_symbol_chars = {x for x in pressed_keys if x in symbol_chars}  # any hotkeys are symbols
                        if 'shift' in pressed_keys and check_single_chars and (
                                check_alphabet_letters or check_symbol_chars):
                            line = 'Type:{}'.format(''.join([x.capitalize() for x in pressed_keys if x != 'shift']))
                            # pressed_keys = []
                        else:
                            line = 'Hotkey {}'.format(' + '.join(pressed_keys))
                    else:
                        line = ''
                    register_hotkey = False
                    if key in pressed_keys:
                        pressed_keys.remove(key)

                print('pressed_keys: {}'.format(pressed_keys))

            # else:
            if line:
                processed_line = break_code + line + break_code
            else:
                processed_line = ''

        for master_key, replacement_keys in replacement_keys_ref.items():
            for replacement_key in replacement_keys:
                processed_line = processed_line.replace(replacement_key, master_key)

        processed_lines.append(processed_line)
        print('processed_line: {}'.format(processed_line))
    else:
        skip = False

    print()
# processed_lines.append(break_code + lines[-1])
print(processed_lines)
processed_lines = ''.join(processed_lines).split(break_code)
processed_lines = [x for x in processed_lines if x]
print()
print()

# consolidate triple clicks
processed_lines_to_remove = []
skip = 0
for index, (tripleA, tripleB, tripleC) in enumerate(
        zip(processed_lines, processed_lines[1:], processed_lines[2:])):
    if skip:
        skip -= 1
    else:
        if 'Left-mouse click' in tripleA and tripleA == tripleB == tripleC:
            skip = 3 - 1  # number of clicks minus one
            processed_lines[index] = 'Triple-click at {}\n'.format(coords_of(tripleA))
            processed_lines_to_remove.append(index + 1)
            processed_lines_to_remove.append(index + 2)
            processed_lines[index + 1] = ''
            processed_lines[index + 2] = ''
for index in processed_lines_to_remove[::-1]:
    processed_lines.pop(index)

# consolidate double clicks
processed_lines_to_remove = []
skip = 0
for index, (pairA, pairB) in enumerate(zip(processed_lines, processed_lines[1:])):
    if skip:
        skip -= 1
    else:
        if 'Left-mouse click' in pairA and pairA == pairB:
            skip = 2 - 1  # number of clicks minus one
            processed_lines[index] = 'Double-click at {}\n'.format(coords_of(pairA))
            processed_lines_to_remove.append(index + 1)
            processed_lines[index + 1] = ''
for index in processed_lines_to_remove[::-1]:
    processed_lines.pop(index)

print(processed_lines)

# consolidate consecutive type commands
typing_indices = [index for index, line in enumerate(processed_lines) if 'Type:' in line]
typing_ranges = consecutive_ranges_of(typing_indices)
print(list(reversed(typing_ranges)))
for typing_range in reversed(typing_ranges):
    if typing_range[0] != typing_range[1]:  # only if range is not a single index
        consolidated_type = ''
        for index in reversed(range(typing_range[0], typing_range[1] + 1)):
            line = processed_lines[index]
            consolidated_type = line.replace('Type:', '') + consolidated_type
            if index != typing_range[0]:
                del processed_lines[index]
        processed_lines[typing_range[0]] = 'Type:{}'.format(consolidated_type)

print(processed_lines)
