# import subprocess
#
# current_machine_id = subprocess.check_output('wmic csproduct get uuid').split('\n')[1].strip()
#
# print(current_machine_id)

import uuid
current_machine_id = uuid.UUID(int=uuid.getnode())
print(current_machine_id)

import zlib

a = "this string needs compressing".encode()
print(a)
a = zlib.compress(a)
print(a)
print(zlib.decompress(a))