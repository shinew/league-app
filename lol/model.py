__doc__ = '''Contains data structures of basic game entities.

'''


import enum


class queue_type(enum.Enum):
    ranked_solo = 'RANKED_SOLO_5x5'
    team_builder_draft = 'TEAM_BUILDER_DRAFT_RANKED_5x5'
    ranked_threes = 'RANKED_TEAM_3x3'
    ranked_fives = 'RANKED_TEAM_5x5'


class season_type(enum.Enum):
    season2016 = 'SEASON2016'
    preseason2016 = 'PRESEASON2016'


class Match(object):
    '''Represents a match.'''

    def __init__(self, match_id, )
