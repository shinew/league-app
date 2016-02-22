from lol.api import APITaskQueue, create_task
import threading
import time


s = APITaskQueue(api_keys=['shine', 'xian', 'wang'], rate_limits=[],
        num_threads=50)

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
    time.sleep(1)
    s.put(create_task(f))

[s.put(create_task(f)) for _ in range(40)]
s.start()
