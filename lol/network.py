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

    def __init__(self, rate_limits=[], queue_limit=None):
        '''Args:
            rate_limits: a list of (num_requests, num_seconds), where we can
                send a max of num_requests within num_seconds. Default to no
                rate limit.
            queue_limit: maximum size of a queue. Default to unlimited.
        '''
        self._queue = collections.deque()
        self._queue_limit = queue_limit
        self._rate_counters = RateCounterPool(rate_limits)
        self._lock = threading.Lock()

    def put(self, tasks):
        '''Adds as many tasks as possible to the queue, and returns the number
        of tasks added. Thread-safe.
        '''
        with self._lock:
            if self._queue_limit is None:
                self._queue.extend(tasks)
                return len(tasks)
            else:
                truncated = tasks[:self._queue_limit - len(self._queue)]
                self._queue.extend(truncated)
                return len(truncated)

    def can_get(self):
        '''Returns:
            - True iff a task is available right now.
            - False iff the queue is empty.
            - An integer indicating the time until the task is ready if there is
                something in the queue.
            - None if the time until the task is ready is unknown.
        Thread-safe.
        '''

        with self._lock:
            now = math.ceil(time.time())
            if self._rate_counters.can_add(now) and len(self._queue) > 0:
                return True
            elif len(self._queue) == 0:
                return False
            else:
                return self._rate_counters.time_until_ready(now)

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
        assert all((len(x) == 2 and x[0] > 0 and x[1] > 0)
                for x in rate_limits), \
                'rate limits must be of type (num_requests, num_seconds).'
        self._rate_counters = [RateCounter(x[0], x[1]) for x in rate_limits]

    def __repr__(self):
        return '\t'.join(x.__repr__() for x in self._rate_counters)

    def can_add(self, now):
        '''Returns True iff a task can be run given the rate limit.'''
        return all(x.can_add(now) for x in self._rate_counters)

    def time_until_ready(self, now):
        '''Returns the time until a task will be ready, in seconds. Returns None
        if uninitialized.
        '''
        return max(x.time_until_ready(now) for x in self._rate_counters)

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

    def time_until_ready(self, now):
        '''Returns the time until a task will be ready, in seconds. Returns None
        if uninitialized.'''
        self._maybe_reset(now)
        if self._start is None:
            return None
        return now - self._start + self._interval

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
            futures = [executor.submit(run_forever(self._fn))
                    for _ in range(self._num_threads)]
            concurrent.futures.as_completed(futures)
