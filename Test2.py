from screeninfo import get_monitors
import hashlib
import time
import pyautogui

for m in get_monitors():
    print(str(m))
monitor_config = str(50*get_monitors())
print(f'monitor_config: {monitor_config}')
display_size = (sum([monitor.width for monitor in get_monitors()]), sum([monitor.height for monitor in get_monitors()]))
tot_height = sum([monitor.height for monitor in get_monitors()])
print(f'total display_size: {display_size}')
print(f'total height: {tot_height}')
print()

monitor_config = str(hashlib.sha256(monitor_config.encode()).hexdigest())
print(f'SHA256 hash: {len(monitor_config)}, {monitor_config}')

from cryptography.fernet import Fernet
# key = Fernet.generate_key()
# print(key)
key = b'EH2HILmaTda7tEAFLJzVlAF8rDzI5byri6vo_bA9xd8='
cipher_suite = Fernet(key)
# encoded_text = cipher_suite.encrypt(b"Hello stackoverflow!")
# print(len(encoded_text), encoded_text)
encoded_text = cipher_suite.encrypt(monitor_config.encode())
print(f'encrypted: {len(encoded_text)}, {encoded_text}')
decoded_text = cipher_suite.decrypt(encoded_text)
# print(decoded_text)
# decoded_text = cipher_suite.decrypt(b'gAAAAABepPGAZr9oonuohr7Qo0Cij7nK1V7wpHo0bLQcPYtJg7SHrQt2VzOI_qzqUB-KIuxsup4kFuLW3O2WxDAtnCfhSN1L3zLwNDBo7PJDjMSySivBjpU=')

# print(decoded_text)