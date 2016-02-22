from lol.api import APITaskQueue, make_task
import threading
import time


s = APITaskQueue(api_keys=['shine', 'xian', 'wang'], rate_limits=[(1, 1), (1, 2)], task_limit=20,
        num_threads=5)

class Counter(object):
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

g = Counter()

@make_task
def f(key=''):
    print('I was passed an API key {}'.format(key))
    print('Called from {:d} at {:.0f}'.format(threading.get_ident(), time.time()))
    with g.lock:
        g.counter += 1
        print('Counter=', g.counter)
    time.sleep(1)
    print('We put', s.put([f, f]), 'tasks.')

s.put([f for _ in range(20)])
s.start()
