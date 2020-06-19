import threading
import time
def test(arr, i):
    # print("%s threading is printed %s, %s"%(threading.current_thread().name, value1, value2))
    arr[i] += 1
    l.append(0)
    # return 'finished'

def test_result(future):
    print(future.result())

if __name__ == "__main__":
    import numpy as np
    from concurrent.futures import ThreadPoolExecutor
    threadPool = ThreadPoolExecutor(max_workers=4)
    l = [2,3,4]
    for i in range(0,10):
        future = threadPool.submit(test, l,2)

#         future.add_done_callback(test_result)
        # print(future.result())
    
    threadPool.shutdown(wait=True)
    print(l)
    print('main finished')