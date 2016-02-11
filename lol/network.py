__doc__ = '''Interface to handle network-related tasks.

'''


import aiohttp
import asyncio
import logging
import math
import queue
import threading
import time

from collections import namedtuple


_logger = logging.getLogger()


class TaskQueue(object):
    '''A generic thread-safe task queue that supports rate limits.

    Provides second-level granularity for rate limiting.

    '''
    def __init__(self, rate_limits=[], task_limit=0):
        '''
        Args:
            rate_limits: a list of (num_requests, num_seconds), where we can send a max of
                num_requests within num_seconds.
            task_limit: maximum number of tasks we should enqueue.
            num_threads: number of threads we want to use.
        '''
        assert all((len(x) == 2 and x[0] > 0 and x[1] > 0) for x in rate_limits), \
                'rate limits must be of type (num_requests, num_seconds).'

        self._queue = queue.Queue(maxsize=task_limit)
        self._rate_counters_lock = threading.Lock()
        self._rate_counters = _RateCounterGroup(rate_limits)

    def put(self, task):
        '''Adds an async task to the queue. If full, returns False, else returns True.

        Thread-safe.

        '''
        try:
            self._queue.put_nowait(task)
        except queue.Full:
            _logger.warning("Failed to add task %s to the full task queue.", task)
            return False
        else:
            return True

    def get(self):
        '''Returns a task iff the caller can execute the task given the time limit, else returns
        None.

        Thread-safe.

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


class _RateCounterGroup(object):
    '''A collection of rate counters.

    Not thread-safe.

    '''
    def __init__(self, rate_limits):
        self._rate_counters = [_RateCounter(x[0], x[1]) for x in rate_limits]

    def __repr__(self):
        return '\t'.join(x.__repr__() for x in self._rate_counters)

    def start(self, now):
        [x.start(now) for x in self._rate_counters]

    def can_add(self, now):
        return all(x.can_add(now) for x in self._rate_counters)

    def increment(self, now):
        [x.increment(now) for x in self._rate_counters]


class _RateCounter(object):
    '''A dummy for storing rate counts.

    Not thread-safe.

    '''
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

    def start(now):
        '''Starts timing from `now`.'''
        self._start = now

    def can_add(self, now):
        '''Returns True iff under the limit.'''
        self._reset(now)
        return self._count < self._limit

    def increment(self, now):
        '''Adds 1 to the counter.'''
        if self._start is None:
            self._start = now
        self._reset(now)
        self._count += 1
