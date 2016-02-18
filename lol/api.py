__doc__ = '''Interface to handle generic API-related functionality.

'''


import threading

from lol.network import TaskQueue, Scheduler


class APIQueueScheduler(object):
    '''Generic interface to send rate-limited API requests.'''

    def __init__(self, api_keys=[], rate_limits=[], task_limit=0, sleep_duration=0.5,
            num_threads=1):
        '''Args:
            api_keys: if this is set, a key will be passed onto the task as a param.
            rate_limits: a list of (num_requests, num_seconds), where we can send a max of
                num_requests within num_seconds for each key.
        '''
        assert all((len(x) == 2 and x[0] > 0 and x[1] > 0) for x in rate_limits), \
                'rate limits must be of type (num_requests, num_seconds).'

        # Scale up the rate limits
        if len(api_keys) >= 2:
            for i in range(len(rate_limits)):
                rate_limits[i] = (rate_limits[i][0] * len(api_keys), rate_limits[i][1])

        self._queue = TaskQueue(rate_limits=rate_limits, task_limit=task_limit)
        self._scheduler = Scheduler(self._check_and_run_task,
                sleep_duration=sleep_duration, num_threads=num_threads)
        self._api_keys = api_keys
        self._need_key = len(api_keys) >= 1
        if self._need_key:
            self._key_counter = 0
            self._key_lock = threading.Lock()

    def put(self, task):
        '''Adds a task to the queue.'''
        return self._queue.put(task)

    def start(self):
        '''Activates the scheduler. Queue should be populated before running this.'''
        self._scheduler.start()

    def _check_and_run_task(self):
        '''Runs a task if available. Returns False iff a task was run.'''
        task = self._queue.get()
        if task:
            assert callable(task), 'Task must be callable with the argument APIQueueScheduler.'
            if self._need_key:
                key = None
                with self._key_lock:
                    key = self._api_keys[self._key_counter]
                    self._key_counter = (self._key_counter + 1) % len(self._api_keys)
                task(self, key=key)
            else:
                task(self)
            self._queue.task_done()
            return False
        else:
            return True
