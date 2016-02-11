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
    '''A generic multithreaded, asynchronous task queue that supports rate limits.

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

        self.rate_limits = rate_limits
        self.task_limit = task_limit

        self._queue = queue.Queue(maxsize=self.task_limit)
        self._rate_counter_lock = threading.Lock()
        now = math.ceil(time.time())
        self._rate_counters = [RateCounter(now, x[1], x[0]) for x in self.rate_limits]

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
        with self._rate_counter_lock:
            now = math.ceil(time.time())
            if all(x.ok(now) for x in self._rate_counters):
                task = None
                try:
                    task = self._queue.get_nowait()
                except queue.Empty:
                    return
                else:
                    [x.increment(now) for x in self._rate_counters]
                    return task


class RateCounter(object):
    '''A dummy for storing rate counts.

    Not thread-safe.

    '''
    def __init__(self, start, interval, limit, count=0):
        self.start = start
        self.interval = interval
        self.limit = limit
        self.count = count

    def __repr__(self):
        return 'RateCounter(start=%s, next=%s, count=%s, limit=%s)' % \
                (self.start, self.start + self.interval, self.count, self.limit)

    def ok(self, now):
        ''' Returns True iff count < limit.'''
        self.reset(now)
        return self.count < self.limit

    def increment(self, now):
        ''' Adds 1 to the counter.'''
        self.reset(now)
        self.count += 1

    def reset(self, now):
        '''Possibly resets the counter.'''
        if now - self.start >= self.interval:
            self.start = now
            self.count = 0
