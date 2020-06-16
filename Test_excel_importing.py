import clipboard
import numpy as np
import time

text = clipboard.paste()  # text will have the content of clipboard
print([text])


# clipboard_text = '1\tA\r\n2\tB\r\n3\tC\r\n4\tD\r\n5\tE\r\n6\tF\r\n'
clipboard_text = '1\tA\talpha\r\n2\tB\tbeta\r\n3\tC\t\r\n4\tD\tgamma\r\n5\tE\tdelta\r\n6\tF\tepsilon\r\n'

excel_list = clipboard_text.split('\r\n')
excel_list = [row.split('\t') for row in excel_list]
excel_list.remove([''])
excel_array = np.array(excel_list)

print(excel_array)