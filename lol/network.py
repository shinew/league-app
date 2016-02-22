__doc__ = '''Multithreaded and thread-safe components.

'''


import collections
import concurrent.futures
import math
import threading
import time


class TaskQueue(object):
    '''A generic thread-safe task queue that supports rate limits.
    Provides rate limiting conservatively rounded to the second.
    '''

    def __init__(self, rate_limits=[], task_limit=None):
        '''Args:
            rate_limits: a list of (num_requests, num_seconds), where we can
                send a max of num_requests within num_seconds. Default to no
                rate limit.
            task_limit: maximum number of tasks we should enqueue. Default to
                unlimited.
        '''
        self._queue = collections.deque()
        self._task_limit = task_limit
        self._rate_counters = RateCounterPool(rate_limits)
        self._lock = threading.Lock()

    def put(self, *tasks):
        '''Adds tasks to the queue. If the queue cannot fit all the tasks, none
        of the tasks will be added, returns False. Else returns True.
        Thread-safe.
        '''
        with self._lock:
            if self._task_limit and len(self._queue) + len(tasks) > self._task_limit:
                return False
            else:
                self._queue.extend(tasks)
                return True

    def empty(self):
        '''Returns True iff no task is available.'''
        with self._lock:
            now = math.ceil(time.time())
            if self._rate_counters.can_add(now) and len(self._queue) > 0:
                return False
            else:
                return True

    def get(self):
        '''Returns a task iff the caller can execute the task given the time
        limit, else returns None. Thread-safe.
        '''
        with self._lock:
            now = math.ceil(time.time())
            if self._rate_counters.can_add(now) and len(self._queue) > 0:
                self._rate_counters.increment(now)
                task = self._queue.popleft()
                return task


class RateCounterPool(object):
    '''A collection of rate counters. Not thread-safe.
    '''

    def __init__(self, rate_limits):
        assert all((len(x) == 2 and x[0] > 0 and x[1] > 0) \
                for x in rate_limits), \
                'rate limits must be of type (num_requests, num_seconds).'
        self._rate_counters = [RateCounter(x[0], x[1]) for x in rate_limits]

    def __repr__(self):
        return '\t'.join(x.__repr__() for x in self._rate_counters)

    def can_add(self, now):
        '''Returns true iff a task can be run given the rate limit.'''
        return all(x.can_add(now) for x in self._rate_counters)

    def increment(self, now):
        '''Automatically starts the timer, and adds 1 to the counters.'''
        for x in self._rate_counters:
            x.increment(now)


class RateCounter(object):
    '''A dummy for storing rate counts. Not thread-safe.'''

    def __init__(self, limit, interval, count=0):
        self._limit = limit
        self._interval = interval
        self._count = count
        self._start = None

    def __repr__(self):
        return 'RateCounter(start=%s, next=%s, count=%s, limit=%s)' % \
                (self._start, self._start + self._interval, self._count,
                        self._limit)

    def can_add(self, now):
        '''Returns true iff a task can be run given the rate limit.'''
        self._maybe_reset(now)
        return self._count < self._limit

    def increment(self, now):
        '''Automatically starts the timer, and adds 1 to the counter.'''
        if self._start is None:
            self._start = now
        self._maybe_reset(now)
        self._count += 1

    def _maybe_reset(self, now):
        if self._start and now - self._start >= self._interval:
            self._start = now
            self._count = 0


class FunctionalThreadPool(object):
    '''A thread pool that will repeatedly run the same function from multiple
    threads.
    '''

    def __init__(self, fn, num_threads=1):
        '''Args:
            num_threads: number of threads to use. Default to 1.
        '''
        assert num_threads > 0, \
                'Must have at least 1 thread for the Scheduler to run.'
        assert callable(fn), 'function must be callable.'
        self._fn = fn
        self._num_threads = num_threads

    def start(self):
        '''Starts running the thread pool.'''
        def run_forever(f):
            def g():
                while True:
                    f()
            return g

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._num_threads) as executor:
            futures = [executor.submit(run_forever(self._fn)) \
                    for _ in range(self._num_threads)]
            concurrent.futures.as_completed(futures)
