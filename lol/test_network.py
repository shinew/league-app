from lol.network import APITaskQueue, make_task
import threading
import time


s = APITaskQueue(api_keys=['shine', 'simon', 'bryan', 'shine2', 'shine3', 'shine4'],
        rate_limits=[(10, 10), (500, 10*60)], queue_limit=1000, num_threads=60)

class Counter(object):
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

g = Counter()

@make_task
def f(key=''):
    print('Called from {:d} at {:.0f}'.format(threading.get_ident(), time.time()))
    with g.lock:
        g.counter += 1
        print('Counter=', g.counter)
    time.sleep(2)
#    print('I was passed an API key {}'.format(key))
    s.put([f, f])

s.put([f for _ in range(60)])
s.start()
