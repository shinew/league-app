___doc___ = '''Tasks for the API.

'''


import lol.api as api
import lol.db as db
import lol.model as model
import lol.riot_queue as queue

from collections import defaultdict


class Task(object):
    '''Generic task.'''

    def _handle_response(self, response):
        (status_type, obj) = response
        if status_type is api.status.ok:
            return obj
        elif status_type is api.status.failed_request:
            queue.add_task(self)


class MatchList(Task):
    '''Pulls the match history of the player and enqueues matches.'''

    def __init__(self, summoner_id):
        self._summoner_id = summoner_id

    def __call__(self, key=''):
        if db.has_summoner_id(self._summoner_id):
            return False

        match_list = self._handle_response(api.MatchList.get(key, self._summoner_id))
        if match_list is None:
            return False

        summoner_champions = self._get_summoner_champions(match_list)
        db.add_summoner_champions(summoner_champions)

        match_ids = [x.match_id for x in match_list \
                if not db.has_match_id(x.match_id)]
        queue.add_tasks([MatchInfo(x) for x in match_ids])
        return True

    def _get_summoner_champions(self, match_list):
        champ_counts = defaultdict(int)
        for match in match_list:
            champ_counts[match.champion_id] += 1
        z = []
        for champ in champ_counts:
            z.append(model.Champion(self._summoner_id, champ, champ_counts[champ]))
        return z


class SummonerTier(Task):
    '''Adds a summoner and her tier.'''

    def __init__(self, summoner_id):
        self._summoner_id = summoner_id

    def __call__(self, key=''):
        tier = self._handle_response(api.SummonerTier.get(key, self._summoner_id))
        if tier is None:
            return False

        summoner = model.Summoner(self._summoner_id, tier)
        db.add_summoner(summoner)
        return True


class MatchInfo(Task):
    '''Pulls the entire match data and enqueues players.'''

    def __init__(self, match_id):
        self._match_id = match_id

    def __call__(self, key=''):
        if db.has_match_id(self._match_id):
            return False

        match = self._handle_response(api.MatchInfo.get(key, self._match_id))
        if match is None:
            return False

        db.add_match(match)

        summoner_ids = [x.summoner_id for x in match.players_stats \
                if not db.has_summoner_id(x.summoner_id)]
        match_list_tasks = [MatchList(x) for x in summoner_ids]
        tier_tasks = [SummonerTier(x) for x in summoner_ids]
        queue.add_tasks([t for ts in zip(match_list_tasks, tier_tasks) for t in ts])
        return True
