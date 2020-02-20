test = ['noah', 'name1', 'noel', 'noel', '', '']

skip = 0
for index, (pairA, pairB) in enumerate(zip(test, test[1:])):
    if skip:
        skip -= 1
    else:
        if pairA and pairA == pairB:
            print(pairA.strip('\n'), 'doubleclick')
            skip = 2 - 1  # number of clicks minus one
