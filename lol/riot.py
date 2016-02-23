__doc__ = '''Riot API calls.

'''


import enum
import logging
import requests

from collections import namedtuple

import lol.model as model


class status(enum.IntEnum):
    ok = 200
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    rate_limit_exceeded = 429
    server_error = 500
    server_unavailable = 503


class RiotRequest(object):
    '''Base class for Riot API calls.'''

    base_url = 'https://na.api.pvp.net'

    @classmethod
    def get(cls, key, **kwargs):
        '''Calls the Riot API and processes result.'''
        constructed_url = cls.base_url + cls.path.format(**kwargs)
        result = requests.get(constructed_url, params={'api_key': key})
        if result.status_code == status.ok:
            try:
                return cls._parse(result.json(), **kwargs)
            except:
             logging.warning('Failed to parse JSON of request %s',
                     constructed_url)
        else:
             logging.warning('Failed request %s with status code %s',
                     constructed_url, result.status_code)

    @classmethod
    def _parse(cls, json, **kwargs):
        '''Processes the JSON request result, if successful.'''
        return NotImplementedError


class SummonerMatches(RiotRequest):
    '''Returns all SoloqQ matches of a summoner in the current season.'''

    path = '/api/lol/{region}/v2.2/matchlist/by-summoner/{summoner_id:d}'

    _match_champion = namedtuple('MatchChampion', ['match_id', 'champion_id'])

    @classmethod
    def get(cls, key, summoner_id):
        return super().get(key, region=model.current_region, summoner_id=summoner_id)

    @classmethod
    def _parse(cls, j_data, region='', summoner_id=0):
        j_matches = j_data['matches']
        matches = []
        for j_match in j_matches:
            if j_match['season'] == model.current_season \
                    and j_match['queue'] == model.ranked_solo:
                matches.append(cls._match_champion(j_match['matchId'], j_match['champion']))
        return matches


class CurrentSummonerTier(RiotRequest):
    '''Returns the current tier of a summoner.'''

    path = '/api/lol/{region}/v2.5/league/by-summoner/{summoner_id:d}'

    @classmethod
    def get(cls, key, summoner_id):
        return super().get(key, region=model.current_region, summoner_id=summoner_id)

    @classmethod
    def _parse(cls, j_data, region='', summoner_id=0):
        j_leagues = j_data[str(summoner_id)]
        for j_league in j_leagues:
            if j_league['queue'] == model.ranked_solo:
                return model.get_tier_id(j_league['tier'])


class MatchData(RiotRequest):
    '''Returns the complete data for a match.'''

    path = '/api/lol/{region}/v2.2/match/{match_id:d}'

    @classmethod
    def get(cls, key, match_id):
        return super().get(key, region=model.current_region, match_id=match_id)

    @classmethod
    def _parse(cls, j_data, region='', match_id=0):
        duration = j_data['matchDuration']
        creation_time = j_data['matchCreation']
