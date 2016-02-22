__doc__ = '''Contains data structures of basic game entities.

'''


import enum


@enum.unique
class queue_type(enum.Enum):
    ranked_solo = 'RANKED_SOLO_5x5'
    team_builder_draft = 'TEAM_BUILDER_DRAFT_RANKED_5x5'
    ranked_threes = 'RANKED_TEAM_3x3'
    ranked_fives = 'RANKED_TEAM_5x5'


@enum.unique
class season_type(enum.Enum):
    season2016 = 'SEASON2016'
    preseason2016 = 'PRESEASON2016'


@enum.unique
class region_type(enum.Enum):
    na = 'na'
    kr = 'kr'
    euw = 'euw'


class Match(object):
    '''Represents a match.'''

    def __init__(self, match_id, duration=0, creation_time=0, red_won = False,
            player_stats=[], red_team_stats=None, blue_team_stats=None):
        self.match_id = match_id
        self.duration = duration
        self.creation_time = creation_time
        self.red_won = red_won
        self.player_stats = player_stats
        self.red_team_stats = red_team_stats
        self.blue_team_stats = blue_team_stats


class Stats(object):
    '''Represents an entity's perspective of a match.'''

    def __init__(self, kills=0, deaths=0, assists=0, damage_dealt=0,
            damage_taken=0, cs=0, gold_earned=0):
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.cs = cs
        self.gold_earned = gold_earned


class PlayerStats(Stats):
    '''Represents one summoner's perspective of a match.'''

    def __init__(self, summoner_id, champion_id=0, won=False, **kwargs):
        super().__init__(**kwargs)
        self.summoner_id = summoner_id
        self.champion_id = champion_id
        self.won = won


class TeamStats(Stats):
    '''Represents a team's perspective of a match.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
