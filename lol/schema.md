# Schema

## match
To store match data.

| name            | type |
| ---             | ---  |
| match_id (key1) | int  |
| season_id       | int  |
| creation_time   | int  |
| duration        | int  |


## game
To iterate over summoners in a match.

| name                               | type |
| ---                                | ---  |
| match_id (key1)                    | int  |
| summoner_id (key2)                 | int  |
| assists                            | int  |
| champion_id                        | int  |
| cs                                 | int  |
| deaths                             | int  |
| division_id                        | int  |
| gold_earned                        | int  |
| kills                              | int  |
| team_damage_dealt                  | int  |
| team_damage_taken                  | int  |
| team_deaths                        | int  |
| team_gold_earned                   | int  |
| team_kills                         | int  |
| won                                | bool |


## summoner
To store summoner data.

| name               | type |
| ---                | ---  |
| summoner_id (key1) | int  |
| last_visited       | int  |
| summoner_name      | str  |


## summoner_match
To iterate over matches of a summoner.

| name               | type |
| ---                | ---  |
| summoner_id (key1) | int  |
| match_id (key2)    | int  |
| summoner_name      | str  |
