import time

t0 = time.time()

var = 'hahah'

for ii in range(1000000):
    test = 'hello-' + str(var) + ' nice to meet you'
    # test = 'hello-{}'.format(var)

t0a = time.time() - t0
print('TIME add: {}s'.format(t0a))

t1 = time.time()

var = 'hahah'

for ii in range(1000000):
    # test = 'hello-' + var
    test = 'hello-{} nice to meet you'.format(var)

t1a = time.time() - t1
print('TIME    : {}s'.format(t1a))

print()

print('ratio: ' + str(t1a / t0a))
