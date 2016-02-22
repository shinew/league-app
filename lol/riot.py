__doc__ = '''Riot API calls.

'''


import enum
import logging
import requests


_logger = logging.getLogger()


@enum.unique
class status_type(enum.IntEnum):
    ok = 200
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    rate_limit_exceeded = 429
    server_error = 500
    server_unavailable = 503


class RiotRequest(object):
    '''Base class for Riot API calls.'''

    BASE_URL = 'https://na.api.pvp.net'

    @classmethod
    def get(cls, key, **kwargs):
        '''Calls the Riot API and processes result.'''
        constructed_url = cls.BASE_URL + cls.PATH.format(**kwargs)
        result = requests.get(constructed_url, params={'api_key': key})
        if result.status_code == status_type.ok:
            return cls.parse(result.json())
        else:
             _logger.warning('Failed request with status code %s',
                     result.status_code)

    @classmethod
    def parse(cls, json):
        '''Processes the JSON request result, if successful.'''
        return NotImplementedError


class MatchesOfSummonerRequest(RiotRequest):
    '''Returns all matches of a summoner.'''

    PATH = '/api/lol/{region}/v2.2/matchlist/by-summoner/{summoner_id:d}'

    @classmethod
    def get(cls, key, summoner_id):
        return super().get(key, region='na', summoner_id=summoner_id)
