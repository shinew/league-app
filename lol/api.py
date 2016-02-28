__doc__ = '''Riot API calls.

'''


import enum
import logging
import requests
import sys

import lol.model as model

@enum.unique
class status(enum.IntEnum):
    ok = 1
    failed_request = 2
    malformed_request = 3

class RiotRequest(object):
    '''Base class for Riot API calls.'''

    base_url = 'https://na.api.pvp.net'

    @classmethod
    def get(cls, key, **kwargs):
        '''Calls the Riot API and processes result.'''
        constructed_url = cls.base_url + cls.path.format(**kwargs)
        try:
            result = requests.get(constructed_url, params={'api_key': key})
        except:
            logging.warning('%s', sys.exc_info())
            return (status.failed_request, None)
        try:
            assert result.status_code == 200
            return (status.ok, cls._parse(result.json(), **kwargs))
        except:
            return (status.malformed_request, None)

    @classmethod
    def _parse(cls, json, **kwargs):
        '''Processes the JSON request result, if successful.'''
        return NotImplementedError


class MatchList(RiotRequest):
    '''Returns all SoloqQ matches of a summoner in the current season.'''

    path = '/api/lol/{region}/v2.2/matchlist/by-summoner/{summoner_id:d}'

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
                matches.append(model.match_champion(j_match['matchId'], j_match['champion']))
        return matches


class SummonerTier(RiotRequest):
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


class MatchInfo(RiotRequest):
    '''Returns the complete data for a match.'''

    path = '/api/lol/{region}/v2.2/match/{match_id:d}'

    @classmethod
    def get(cls, key, match_id):
        return super().get(key, region=model.current_region, match_id=match_id)

    @classmethod
    def _parse(cls, j_data, region='', match_id=0):
        duration = j_data['matchDuration']
        creation_time = j_data['matchCreation']

        players = [cls._parse_player_stats(x,y) for (x,y) in \
                zip(j_data['participants'], j_data['participantIdentities'])]
        assert len(players) == 10, 'should have 10 players.'

        winning_players = [x for x in players if x.won]
        losing_players = [x for x in players if not x.won]
        winning_team = cls._aggregate_team_stats(winning_players)
        losing_team = cls._aggregate_team_stats(losing_players)

        match = model.Match(match_id, duration=duration, creation_time=creation_time,
                players_stats=players, winning_team_stats=winning_team, losing_team_stats=losing_team)
        return match

    @classmethod
    def _parse_player_stats(cls,  j_participant, j_participant_identity):
        pstats = model.PlayerStats(0)
        pstats.summoner_id = j_participant_identity['player']['summonerId']
        pstats.champion_id = j_participant['championId']

        j_participant_stats = j_participant['stats']
        pstats.kills = j_participant_stats['kills']
        pstats.deaths = j_participant_stats['deaths']
        pstats.assists = j_participant_stats['assists']
        pstats.damage_dealt = j_participant_stats['totalDamageDealtToChampions']
        pstats.damage_taken = j_participant_stats['totalDamageTaken']
        pstats.gold = j_participant_stats['goldEarned']
        pstats.cs = j_participant_stats['minionsKilled']
        pstats.won = j_participant_stats['winner']
        return pstats

    @classmethod
    def _aggregate_team_stats(cls, players):
        tstats = model.TeamStats()
        stats = ['kills', 'deaths', 'assists', 'damage_dealt', 'damage_taken', 'cs', 'gold']
        for stat in stats:
            setattr(tstats, stat, sum(getattr(x, stat) for x in players))
        return tstats
