from lol.api import APITaskQueue, Task
import threading
import time


s = APITaskQueue(api_keys=['shine', 'xian', 'wang'], rate_limits=[(1, 1), (5, 10)],
        num_threads=20)

class Counter(object):
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

g = Counter()

def f(key=''):
    print('I was passed an API key {}'.format(key))
    print('Called from {:d} at {:.0f}'.format(threading.get_ident(), time.time()))
    with g.lock:
        g.counter += 1
        print('Counter={:d}'.format(g.counter))
    time.sleep(2)
    s.put(Task(f))

[s.put(Task(f)) for _ in range(40)]
s.start()
