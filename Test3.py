lines = list(range(10))

for line in lines:
    print(line)
    if line == 4:
        del lines[5:]
