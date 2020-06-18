import time

def imported_func():
    print('this was imported')


class ImportedClass:
    def __init__(self):
        print('this is from imported class init')

    def do_it(self):
        print('this if from the class do it')


if __name__ == '__main__':
    imported_func()
    ImportedClass().do_it()
    # class