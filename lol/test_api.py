from lol.api import APIQueueScheduler
import threading
import time

s = APIQueueScheduler(api_keys=['shine', 'wang'], rate_limits=[(10, 20)], num_threads=3,
        sleep_duration=0.1)

def f(key):
    print('I was passed an API key {}'.format(key))
    print('Called from {:d} at {:.0f}'.format(threading.get_ident(), time.time()))
    s.put(f)

[s.put(f) for _ in range(3)]
s.start()
