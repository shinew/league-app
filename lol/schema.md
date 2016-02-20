# SCHEMA
## season
To store season data.

| season_id (key1) | int |
| season_name      | str |

## season_match
To iterate over all matches of a season.

| season_id (key1) | int |
| match_id (key2)  | int |

## match
To store match data.

| match_id (key1) | int |
| season_id       | int |
| creation_time   | int |
| duration        | int |

## game
To iterate over summoners in a match.

| match_id (key1)                    | int  |
| summoner_id (key2)                 | int  |
| assists                            | int  |
| champion_id                        | int  |
| cs                                 | int  |
| deaths                             | int  |
| gold_earned                        | int  |
| kills                              | int  |
| magic_damage_dealt_to_champions    | int  |
| magic_damage_taken                 | int  |
| physical_damage_dealt_to_champions | int  |
| physical_damage_taken              | int  |
| team_damage_dealt                  | int  |
| team_damage_taken                  | int  |
| team_deaths                        | int  |
| team_gold_earned                   | int  |
| team_gold_earned                   | int  |
| team_kills                         | int  |
| true_damage_dealt_to_champions     | int  |
| true_damage_taken                  | int  |
| won                                | bool |

## summoner
To store summoner data.

| summoner_id (key1) | int |
| last_visited       | int |
| summoner_name      | str |

## summoner_match
To iterate over matches of a summoner.

| summoner_id (key1) | int |
| match_id (key2)    | int |
| summoner_name      | str |
