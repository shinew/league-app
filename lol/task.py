___doc___ = '''Tasks for the API.

'''


import lol.api as api
import lol.db as db
import lol.model as model
import lol.riot_queue as queue

from collections import defaultdict
from functools import partial


def create_task(f):
    def g(*args, **kwargs):
        return partial(f, *args, **kwargs)
    return g


@create_task
def add_match_list(summoner_id, key=''):
    if db.has_summoner_id(summoner_id):
        return False

    match_list = api.MatchList.get(key, summoner_id)
    if match_list is None:
        return False

    summoner_champions = _get_summoner_champions(match_list, summoner_id)
    db.add_summoner_champions(summoner_champions)

    queue.add_task(add_summoner_tier(summoner_id))

    match_ids = [x.match_id for x in match_list \
            if not db.has_match_id(x.match_id)]
    queue.add_tasks([add_match_info(x) for x in match_ids])
    return True


@create_task
def add_summoner_tier(summoner_id, key=''):
    tier = api.SummonerTier.get(key, summoner_id)
    if tier is None:
        return False

    summoner = model.Summoner(summoner_id, tier)
    db.add_summoner(summoner)
    return True


@create_task
def add_match_info(match_id, key=''):
    if db.has_match_id(match_id):
        return False

    match = api.MatchInfo.get(key, match_id)
    if match is None:
        return False

    db.add_match(match)

    summoner_ids = [x.summoner_id for x in match.players_stats \
            if not db.has_summoner_id(x.summoner_id)]
    queue.add_tasks([add_match_list(x) for x in summoner_ids])
    return True


def _get_summoner_champions(match_list, summoner_id):
    champ_counts = defaultdict(int)
    for match in match_list:
        champ_counts[match.champion_id] += 1
    z = []
    for champ in champ_counts:
        z.append(model.Champion(summoner_id, champ, champ_counts[champ]))
    return z
