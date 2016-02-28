___doc___ = '''Tasks for the API.

'''


import lol.api as api
import lol.db as db
import lol.model as model
import lol.queue as queue

from collections import defaultdict
from functools import partial


def make_task(f):
    def g(*args, **kwargs):
        return partial(f, *args, **kwargs)
    return g


@make_task
def match_list(summoner_id, key=''):
    match_list = api.MatchList.get(key, summoner_id)
    if match_list is None:
        return

    summoner_champions = _get_summoner_champions(match_list)
    db.add_summoner_champions(summoner_champions)

    queue.add_task(champion_tier(summoner_id))

    match_ids = [match.match_id for match in match_list]
    queue.add_tasks([match_data(x) for x in match_ids])


@make_task
def champion_tier(summoner_id, key=''):
    tier = api.SummonerTier.get(key, summoner_id)
    if tier is None:
        return
    summoner = model.Summoner(summoner_id, tier)
    db.add_summoner(Summoner)


@make_task
def match_data(match_id, key=''):
    match = api.MatchInfo()


def _get_summoner_champions(match_list):
    champ_counts = defaultdict(int)
    for match in match_list:
        champ_counts[match.champion_id] += 1
    z = []
    for champ in champ_counts:
        z.append(model.Champion(summmoner_id, champ, champ_counts[champ]))
    return z
