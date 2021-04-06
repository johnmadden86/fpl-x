from fpl import FPL, utils
from prettytable import PrettyTable
import aiohttp
import asyncio
from os import environ

from fpl.models import h2h_league

teams = {}


async def main():
    positions = {
        '1': 'GK',
        '2': 'D',
        '3': 'M',
        '4': 'F'
    }
    player_table = PrettyTable()
    player_table.field_names = ['ID', 'Player', 'Form', 'Value', 'Minutes', 'Price']
    # player_table.align['Player'] = '1'
    async with aiohttp.ClientSession() as session:
        fpl_session = FPL(session)
        await fpl_session.login()
        current_gameweek = await utils.get_current_gameweek(session)
        players = await fpl_session.get_players()
        teams_ = await fpl_session.get_teams()
        h2h_league = await fpl_session.get_h2h_league(1034169)

        print(f"Gameweek {current_gameweek}")
        gw_fixtures = await h2h_league.get_fixtures(gameweek=current_gameweek)
        for fixture in gw_fixtures:
            v = f'{await fixture.points_1} - {await fixture.points_2}'
            print(f"{fixture.entry_1_player_name} {v} {fixture.entry_2_player_name}")
        await h2h_league.get_table(phase=4)
        await h2h_league.get_table()
        print(f"Gameweek {current_gameweek + 1}")
        next_gw_fixtures = await h2h_league.get_fixtures(gameweek=current_gameweek + 1)
        for fixture in next_gw_fixtures:
            print(f"{fixture.entry_1_player_name} v {fixture.entry_2_player_name}")
        exit()

        # for team in teams_:
        #     print(team.short_name, await team.threat_for, await team.threat_against(players),
        #           await team.threat_for - await team.threat_against(players))
        # exit()

        user = await fpl_session.get_user(4520195)
        picks = await user.get_picks(current_gameweek)
        picks = picks.values()
        picks = [p for p in picks][0]
        picks = [p['element'] for p in picks]
        for player in players:
            if player.id in picks:
                player.web_name = f"** {player.web_name}"
            points_per_goal = 8 - player.element_type
            player.summary = await fpl_session.get_player_summary(player.id)
            attack_ratings = []
            weights = []
            # noinspection PyUnresolvedReferences
            for game in player.summary.history:
                try:
                    minutes = game['minutes']
                    # if minutes == 0:
                    #     raise ZeroDivisionError
                    power = 1 + game['round'] / 10
                    weight = power ** power
                    attack_rating = (float(game['creativity']) * 3) * weight
                    attack_rating += (float(game['threat']) * points_per_goal) * weight
                    # while minutes <= 45:
                    #     attack_rating += attack_rating
                    #     minutes += 15
                    # if game['opponent_team'] not in (10, 11) and minutes > 0:
                    attack_ratings.append(attack_rating)
                    weights.append(weight)
                except ZeroDivisionError:
                    pass
            try:
                player.form = sum(attack_ratings) / sum(weights)
            except ZeroDivisionError:
                player.form = 0
            finally:
                player.value = player.form / (player.now_cost / 10)
                try:
                    teams[player.team] += player.form
                except KeyError:
                    teams[player.team] = player.form
    top_performers = sorted(players, key=lambda x: x.form, reverse=True)
    # top_performers = filter(lambda x: x.id in picks
    #                                   or x.id in (226, 369)
    #                         , top_performers)
    # top_performers = filter(lambda x: x.form > 0, top_performers)
    # top_performers = filter(lambda x: x.goals_scored > 2, top_performers)
    # top_performers = filter(lambda x: x.element_type == 4, top_performers)
    # top_performers = filter(lambda x: x.element_type == 3
    #                         and x.now_cost <= 68, top_performers)
    # top_performers = filter(lambda x:
    #                         x.element_type == 2 and x.now_cost <= 67
    #                         or x.element_type == 3 and x.now_cost <= 62
    #                         or x.element_type == 4 and x.now_cost <= 86
    #                         , top_performers)
    top_performers = filter(lambda x: x.minutes > 225, top_performers)
    top_performers = filter(lambda x: x.team in (
        1,  # ARS
        2,  # AVL
        3,  # BHA
        4,  # BUR
        5,  # CHE
        6,  # CRY
        7,  # EVE
        8,  # FUL
        9,  # LEI
        10,  # LEE
        11,  # LIV
        12,  # MCI
        13,  # MUN
        14,  # NEW
        15,  # SHU
        16,  # SOU
        17,  # TOT
        18,  # WBA
        19,  # WHU
        20  # WOL
    ), top_performers)
    # top_performers = filter(lambda x: x.team == 12, top_performers)
    for player in top_performers:
        player_table.add_row([
            player.id, f"{player.web_name} ({positions[str(player.element_type)]})",
            round(player.form),
            round(player.value, 1), player.minutes, round(player.now_cost / 10, 1)])
    print(player_table)

    # for k, v in teams.items():
    #     print(utils.team_converter(k), round(v/25))


async def head_to_head():
    league_id = 902521
    async with aiohttp.ClientSession() as session:
        fpl_session = FPL(session)
        await fpl_session.login(environ['EMAIL'], environ['FPL_PASSWORD'])
        league = await fpl_session.get_h2h_league(league_id)

        league_table = PrettyTable()
        league_table.field_names = ['Rank', 'Team', 'Played', 'Won', 'Drawn', 'Lost', 'FPL Points', 'League Points']
        for entry in league.standings['results']:
            team = await fpl_session.get_user(entry['entry'], return_json=True)
            if entry['rank'] > entry['last_rank']:
                r = '-'
            elif entry['rank'] == entry['last_rank']:
                r = '='
            else:
                r = '+'
            league_table.add_row([
                f"{entry['rank']}. ({r})",
                f"{entry['player_name'].title()} ({entry['entry_name']})",
                entry['matches_played'],
                entry['matches_won'],
                entry['matches_drawn'],
                entry['matches_lost'],
                entry['points_for'],
                entry['matches_won'] * 2 + entry['matches_drawn'],
            ])
        league_table.sort_by = ('League Points', 'FPL Points')
        print(league_table)
        fixtures = await league.get_fixtures()
        print(fixtures)


# asyncio.run(main())
asyncio.get_event_loop().run_until_complete(main())
# asyncio.run(head_to_head())
exit()
