__doc__ = '''Database-specific logic here. All functions are thread-safe.

'''


import threading
import lol.model as model
import lol.config as config


def with_lock(f):
    def g(*args, **kwargs):
        with _lock:
            f(*args, **kwargs)
    return g


@with_lock
def add_match(match):
    assert type(match) is model.Match, 'expected a Match object.'
    _match_ids.add(match.match_id)


@with_lock
def add_summoner(summoner):
    assert type(summoner) is model.Summoner, 'expected a Summoner object.'
    _summoner_ids.add(summoner.summoner_id)


@with_lock
def add_summoner_champions(champions):
    assert all(type(x) is model.Champion for x in champions), \
            'expected Champion objects.'


@with_lock
def has_summoner_id(summoner_id):
    return summoner_id in _summoner_ids


@with_lock
def has_match_id(match_id):
    return match_id in _match_ids


#TODO(shine): load has_* methods on start-up
_lock = threading.Lock()
_match_ids = set()
_summoner_ids = set()
