import lol.config as config
import lol.task as task

assert task.add_match_info(2077358662)(key=config.API_KEYS[0])
assert task.add_match_list(48675742)(key=config.API_KEYS[0])
assert task.add_summoner_tier(48675742)(key=config.API_KEYS[0])
