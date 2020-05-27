import concurrent.futures
import time


def do_something(seconds, say):
    print(f'Sleeping {seconds}, {say} second(s)...')
    time.sleep(seconds)
    return f'Done Sleeping...{seconds}, {say}'

if __name__ == '__main__':
    start = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        say = [5, 4, 3, 2, 1]
        secs = reversed(say)

        results = executor.map(do_something, secs, say)

    for result in results:
        print(result)

    finish = time.perf_counter()

    print(f'Finished in {round(finish - start, 2)} second(s)')