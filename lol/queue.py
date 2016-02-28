___doc___ = '''The Riot task queue.

'''


import lol.config as config
import lol.network as network


def add_task(t):
    _riot_queue.put([t])


def add_tasks(ts):
    _riot_queue.put(ts)


def start():
    _riot_queue.start()


_riot_queue = network.APITaskQueue(api_keys=config.API_KEYS,
        rate_limits=[(10, 10), (500, 10*60)], queue_limit=1000, num_threads=30)
