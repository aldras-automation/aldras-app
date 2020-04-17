import time

loop_num = 1000000

var = 'asdf'
var1 = 'isuhsdfkj'
var2 = 'diwn 2skj'

t0 = time.time()
for _ in range(loop_num):
    # test = str(var)+'yeah'
    test = var+var1+var2
    # test = '{}yeah{}{}'.format(var, var, var)
    # test = ''.join([str(var),'yeah'])
t0a = time.time() - t0
print('TIME add: {}s'.format(t0a))

t1 = time.time()
for _ in range(loop_num):
    # test = 'hello-' + var
    test = f'{var}{var1}{var2}'
t1a = time.time() - t1
print('TIME    : {}s'.format(t1a))

print()

print('ratio: ' + str((t1a / t0a) - 1))
