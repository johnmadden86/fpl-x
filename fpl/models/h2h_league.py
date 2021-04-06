from async_property import async_cached_property, async_property
import asyncio

from ..constants import API_URLS
from ..utils import fetch, logged_in

from prettytable import PrettyTable


class H2HLeague:
    """
    A class representing a H2H league in the Fantasy Premier League.

    Basic usage:
    #   >>> from fpl import FPL
    #   >>> import aiohttp
    #   >>> import asyncio
    #   >>>
    #   >>> async def main():
    #   ...     async with aiohttp.ClientSession() as session:
    #   ...         fpl = FPL(session)
    #   ...         await fpl.login()
    #   ...         h2h_league = await fpl.get_h2h_league(760869)
    #   ...     print(h2h_league)
    #   ...
    #   >>> asyncio.run(main())
      League 760869 - 760869
    """

    def __init__(self, league_information, session):
        self._session = session
        for k, v in league_information.items():
            setattr(self, k, v)

    async def get_fixtures(self, gameweek=None, user=None, phase=None):
        """Returns a list of fixtures / results of the H2H league.

        Information is taken from e.g.:
            https://fantasy.premierleague.com/api/leagues-h2h-matches/league/946125/

        :param gameweek: (optional) The gameweek of the fixtures / results.
        :param user: (optional) The user id
        :param phase: (optional) Phase (1-4)
        :type gameweek: string or int
        :rtype: list
        """
        if not self._session:
            return []

        if not logged_in(self._session):
            raise Exception(
                "Not authorised to get H2H fixtures. Log in first.")

        params = {"page": 1}
        if gameweek:
            params.update({"event": gameweek})
        if user:
            params.update({"entry": user})

        has_next = True
        results = []
        while has_next:
            fixtures = await fetch(
                self._session, API_URLS["league_h2h_fixtures"].format(self.id), params=params)
            results.extend(fixtures["results"])

            has_next = fixtures["has_next"]
            params["page"] += 1

        phase_start = 1
        phase_end = 38
        if phase:
            phase_start = (phase - 1) * 9 + 1
            phase_end = phase * 9
            # if phase == 4:
            #     phase_end = 30
        results = [result for result in results if phase_start <= result["event"] <= phase_end]

        results = [H2HFixture(result, self._session) for result in results]

        return results

    @async_cached_property
    async def standings(self):
        results = []
        has_next = True
        page = 1

        while has_next:
            standings = (await asyncio.ensure_future(
                fetch(self._session,
                      API_URLS["league_h2h_standings"].format(self.id, page))))["standings"]
            results.extend(standings["results"])
            has_next = standings["has_next"]
            page += 1

        return results

    @async_cached_property
    async def entries(self):
        return [{
            "id": user["entry"],
            "player_name": user["player_name"],
            "team_name": user["entry_name"]
        } for user in await self.standings]

    async def get_table_entry(self, user, phase=None):
        table_entry = {
            "Name": f'{user["player_name"]} ({user["team_name"]})',
            "W": 0,
            "D": 0,
            "L": 0,
            "FPL points": 0,
            "H2H points": 0
        }
        fixtures = await self.get_fixtures(user=user["id"], phase=phase)
        for fixture in fixtures:
            if fixture.entry_1_entry == user["id"]:
                table_entry["W"] += await fixture.win_1
                table_entry["D"] += await fixture.draw_1
                table_entry["L"] += await fixture.loss_1
                table_entry["FPL points"] += await fixture.points_1
                table_entry["H2H points"] += await fixture.total_1
            elif fixture.entry_2_entry == user["id"]:
                table_entry["W"] += await fixture.win_2
                table_entry["D"] += await fixture.draw_2
                table_entry["L"] += await fixture.loss_2
                table_entry["FPL points"] += await fixture.points_2
                table_entry["H2H points"] += await fixture.total_2
        return table_entry

    async def get_table(self, phase=None):
        table = PrettyTable()
        table.field_names = ["Name", "W", "D", "L", "FPL points", "H2H points"]
        table_data = []
        for entry in await self.entries:
            table_row = await self.get_table_entry(entry, phase)
            table_data.append(list(table_row.values()))
        table_data.sort(key=lambda x: (x[-1], x[-2]), reverse=True)
        for row in table_data:
            table.add_row(row)
        print(table)

    def __str__(self):
        return f"{self.name} - {self.id}"


class H2HFixture:
    def __init__(self, fixture_information, session):
        self._session = session
        for k, v in fixture_information.items():
            setattr(self, k, v)

    async def _score_helper(self, event, entry):
        if event <= 45:
            picks = await fetch(self._session, API_URLS["user_picks"].format(entry, event))
            entry_history = picks["entry_history"]
            return entry_history["points"] - entry_history["event_transfers_cost"]
        else:
            return 0

    @async_cached_property
    async def points_1(self):
        return self.entry_1_points
        # event = self.event
        # if event <= 29:
        #     return self.entry_1_points
        # else:
        #     return await self._score_helper(event + 9, self.entry_1_entry)

    @async_cached_property
    async def points_2(self):
        return self.entry_2_points
        # event = self.event
        # if event <= 29:
        #     return self.entry_2_points
        # else:
        #     return await self._score_helper(event + 9, self.entry_2_entry)

    @async_cached_property
    async def win_1(self):
        return (await self.points_1) > (await self.points_2)

    @async_cached_property
    async def win_2(self):
        return (await self.points_1) < (await self.points_2)

    @async_cached_property
    async def draw_1(self):
        return 0 < (await self.points_1) == (await self.points_2)

    @async_cached_property
    async def draw_2(self):
        return await self.draw_1

    @async_cached_property
    async def loss_1(self):
        return await self.win_2

    @async_cached_property
    async def loss_2(self):
        return await self.win_1

    @async_cached_property
    async def total_1(self):
        return (await self.win_1 * 3) + (await self.draw_1)

    @async_cached_property
    async def total_2(self):
        return (await self.win_2 * 3) + (await self.draw_2)

