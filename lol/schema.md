# Schema

## player_stats
A player's perspective on a match he has played in.

| name                     | type |
| ---                      | ---  |
| match_id (key1, fkey)    | int  |
| summoner_id (key2, fkey) | int  |
| champion_id              | int  |
| won                      | bool |
| kills                    | int  |
| deaths                   | int  |
| assists                  | int  |
| damage_dealt             | int  |
| damage_taken             | int  |
| cs                       | int  |
| gold_earned              | int  |

## match
A match's player-agnostic data.

| name                      | type |
| ---                       | ---  |
| match_id (key1)           | int  |
| creation_time             | int  |
| duration                  | int  |
| win_team_kills            | int  |
| winning_team_deaths       | int  |
| winning_team_assists      | int  |
| winning_team_damage_dealt | int  |
| winning_team_damage_taken | int  |
| winning_team_cs           | int  |
| winning_team_gold_earned  | int  |
| losing_team_kills         | int  |
| losing_team_deaths        | int  |
| losing_team_assists       | int  |
| losing_team_damage_dealt  | int  |
| losing_team_damage_taken  | int  |
| losing_team_cs            | int  |
| losing_team_gold_earned   | int  |

## summoner

| name               | type |
| ---                | ---  |
| summoner_id (key1) | int  |
| tier_id            | int  |

## champion

| name                     | type |
| ---                      | ---  |
| summoner_id (key1, fkey) | int  |
| champion_id (key2)       | int  |
| games_played             | int  |

# Queries

## Games played

No filter: SELECT SUM(games_played) FROM champion / SELECT COUNT(\*) FROM summoner

By tier:

SELECT SUM(champion.games_played)
FROM summoner INNER JOIN champion
ON summoner.summoner_id = champion.summoner_id
GROUP BY summoner.tier_id
WHERE summoner.tier_id = %s /

SELECT COUNT(\*)
FROM summoner
GROUP BY tier_id
WHERE tier_id = %s

## Win rate

(for tier & champion)

SELECT COUNT(\*)
FROM game
WHERE champion_id = %s [AND tier_id = %s] AND won = TRUE /

SELECT COUNT(\*)
FROM game
GROUP BY champion_id, tier_id
WHERE champion_id = %s AND tier_id = %s

## Gold earned

(for tier & champion)

SELECT AVERAGE(gold_earned)
FROM game
WHERE [AND champion_id = %s] [AND tier_id = %s]

## Kill contribution

(for tier & champion)

SELECT AVERAGE(
    CASE WHEN game.won = match.winning_won
        THEN kills/match.winning_team_kills
        DEFAULT THEN kills/match.losing_team_kills
)
FROM game
GROUP BY champion_id, tier_id
WHERE champion_id = %s AND tier_id = %s
