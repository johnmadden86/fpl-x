API_BASE_URL = "https://fantasy.premierleague.com/api/"

API_URLS = {
    "best-classic-private-leagues": "()stats/best-classic-private-leagues/".format(API_BASE_URL),
    "dream_team": "{}dream-team/{{}}".format(API_BASE_URL),
    "event-status": "()event-status".format(API_BASE_URL),
    "fixtures": "{}fixtures/".format(API_BASE_URL),
    "gameweeks": "{}events/".format(API_BASE_URL),
    "gameweek_live": "{}event/{{}}/live".format(API_BASE_URL),
    "league_classic": "{}leagues-classic/{{}}/standings/".format(API_BASE_URL),
    "league_h2h": "{}leagues-h2h/{{}}".format(API_BASE_URL),
    "league_h2h_standings": "{}leagues-h2h/{{}}/standings".format(API_BASE_URL),
    "league_h2h_fixtures": "{}leagues-h2h-matches/league/{{}}/".format(API_BASE_URL),
    "most-valuable-teams": "()stats/most-valuable-teams/".format(API_BASE_URL),
    "player": "{}element-summary/{{}}/".format(API_BASE_URL),
    "static": "{}bootstrap-static/".format(API_BASE_URL),
    "transfers": "{}transfers/".format(API_BASE_URL),
    "user": "{}entry/{{}}/".format(API_BASE_URL),
    "user_cup": "{}entry/{{}}/cup/".format(API_BASE_URL),
    "user_history": "{}entry/{{}}/history/".format(API_BASE_URL),
    "user_picks": "{}entry/{{}}/event/{{}}/picks/".format(API_BASE_URL),
    "user_team": "{}my-team/{{}}/".format(API_BASE_URL),
    "user_transfers": "{}entry/{{}}/transfers/".format(API_BASE_URL),
    "user_latest_transfers": "{}entry/{{}}/transfers-latest/".format(API_BASE_URL),
    "watchlist": "{}watchlist/".format(API_BASE_URL),
    "me": "{}me/".format(API_BASE_URL)
}

PICKS_FORMAT = "{} {}{}"
MYTEAM_FORMAT = "{}{}"

MIN_GAMEWEEK = 1
MAX_GAMEWEEK = 47