import lol.config as config
import lol.task as task

assert task.MatchInfo(2077358662)(key=config.API_KEYS[0])
assert task.MatchList(48675742)(key=config.API_KEYS[0])
assert task.SummonerTier(48675742)(key=config.API_KEYS[0])
