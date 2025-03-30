from balldontlie import BalldontlieAPI
from env_values import nba_results_api_key
from datetime import date, timedelta

api = BalldontlieAPI(api_key=nba_results_api_key)

type_of_days = ["в понедельник", "во вторник", "в среду", "в четверг", "в пятницу", "в субботу", "в воскресенье"]


async def get_nba_games():
    n = date.today().weekday()
    days_data = []

    for i in range(n + 1):
        games = api.nba.games.list(dates=[date.today() - timedelta(days=n - i)])
        games_this_day = games.model_dump().get("data", [])

        day_games = []
        for game in games_this_day:
            day_games.append({
                "home_team": game.get("home_team", {}).get("full_name", ""),
                "home_team_score": int(game.get("home_team_score", 0)),
                "visitor_team": game.get("visitor_team", {}).get("full_name", ""),
                "visitor_team_score": int(game.get("visitor_team_score", 0))
            })

        days_data.append({
            "title": type_of_days[i],
            "games": day_games
        })
    return days_data
