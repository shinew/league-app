__doc__ = '''Interface to handle network-related functionality.

'''


import logging
import math
import queue
import threading
import time


_logger = logging.getLogger()


class TaskQueue(object):
    '''A generic thread-safe task queue that supports rate limits.
    Provides rate limiting conservatively rounded to the second.
    '''

    def __init__(self, rate_limits=[], task_limit=0):
        '''Args:
            rate_limits: a list of (num_requests, num_seconds), where we can send a max of
                num_requests within num_seconds.
            task_limit: maximum number of tasks we should enqueue. Default to unlimited.
        '''

        self._queue = queue.Queue(maxsize=task_limit)
        self._rate_counters_lock = threading.Lock()
        self._rate_counters = RateCounterGroup(rate_limits)

    def put(self, task):
        '''Adds an async task to the queue. If full, returns False, else returns True.
        Thread-safe.
        '''

        try:
            self._queue.put_nowait(task)
        except queue.Full:
            _logger.warning('Failed to add task %s to the full task queue.', task)
            return False
        else:
            return True

    def get(self):
        '''Returns a task iff the caller can execute the task given the time limit, else returns
        None. Thread-safe.
        '''

        with self._rate_counters_lock:
            now = math.ceil(time.time())
            if self._rate_counters.can_add(now):
                task = None
                try:
                    task = self._queue.get_nowait()
                except queue.Empty:
                    return
                else:
                    self._rate_counters.increment(now)
                    return task

    def task_done(self):
        '''Indicates a previously gotten task has completed.'''

        self._queue.task_done()


class RateCounterGroup(object):
    '''A collection of rate counters. Not thread-safe.
    '''

    def __init__(self, rate_limits):
        assert all((len(x) == 2 and x[0] > 0 and x[1] > 0) for x in rate_limits), \
                'rate limits must be of type (num_requests, num_seconds).'
        self._rate_counters = [RateCounter(x[0], x[1]) for x in rate_limits]

    def __repr__(self):
        return '\t'.join(x.__repr__() for x in self._rate_counters)

    def can_add(self, now):
        return all(x.can_add(now) for x in self._rate_counters)

    def increment(self, now):
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
                (self._start, self._start + self._interval, self._count, self._limit)

    def _reset(self, now):
        '''Possibly resets the counter.'''

        if self._start and now - self._start >= self._interval:
            self._start = now
            self._count = 0

    def can_add(self, now):
        '''Returns True iff under the limit.'''

        self._reset(now)
        return self._count < self._limit

    def increment(self, now):
        '''Automatically starts the timer, and adds 1 to the counter.'''

        if self._start is None:
            self._start = now
        self._reset(now)
        self._count += 1


class Scheduler(object):
    '''A generic scheduler that will keep running the same function infinite times on multiple
    threads.
    '''

    def __init__(self, func, sleep_duration=0.5, num_threads=1):
        assert num_threads > 0, \
                'Must have at least 1 thread for the Scheduler to run.'
        assert callable(func), 'func must be callable.'
        self._func = func
        self.sleep_duration = sleep_duration
        self._num_threads = num_threads

    def start(self):
        for _ in range(self._num_threads):
            FunctionalThread(self._func, sleep_duration=self.sleep_duration).start()


class FunctionalThread(threading.Thread):
    '''A thread that can be passed in a function to be called once in a while.'''

    def __init__(self, func, sleep_duration=0.5):
        '''Args:
            func: a function that returns True if it wants to keep running without sleeping.
            sleep_duration: how long this should sleep before re-running.
        '''

        assert callable(func), 'func must be callable.'
        super().__init__()
        self._func = func
        self._sleep_duration = sleep_duration

    def run(self):
        '''Override.'''

        while True:
            keep_running = self._func()
            if not keep_running:
                time.sleep(self._sleep_duration)
