from typing import Union
from pydantic import BaseModel

# Base de données factice des équipes de F1
f1_teams = [
    {"team": "Mercedes", "drivers": ["Lewis Hamilton", "George Russell"]},
    {"team": "Red Bull", "drivers": ["Max Verstappen", "Sergio Perez"]},
    {"team": "Ferrari", "drivers": ["Charles Leclerc", "Carlos Sainz"]},
     {"team": "Mercedes", "drivers": ["Lewis Hamilton", "George Russell"]},
    {"team": "Red Bull", "drivers": ["Max Verstappen", "Sergio Perez"]},
    {"team": "Ferrari", "drivers": ["Charles Leclerc", "Carlos Sainz"]},
    {"team": "McLaren", "drivers": ["Lando Norris", "Oscar Piastri"]},
    {"team": "Aston Martin", "drivers": ["Fernando Alonso", "Lance Stroll"]},
    {"team": "Alpine", "drivers": ["Esteban Ocon", "Pierre Gasly"]},
    {"team": "Williams", "drivers": ["Alexander Albon", "Logan Sargeant"]},
    {"team": "Haas", "drivers": ["Kevin Magnussen", "Nico Hülkenberg"]},
    {"team": "AlphaTauri", "drivers": ["Daniel Ricciardo", "Yuki Tsunoda"]},
    {"team": "Sauber", "drivers": ["Valtteri Bottas", "Zhou Guanyu"]},
]

def get_all_teams_from_fake_db() -> list:
    """Retourne la liste des équipes de F1."""
    return f1_teams

def get_team_from_fake_db(team_name: str) -> Union[dict, None]:
    """Retourne une équipe spécifique en fonction de son nom."""
    for f1_team in f1_teams:
        if team_name.lower() == f1_team.get("team").lower():
            return f1_team
    return None


def create_team_in_fake_db(team: dict):
    """Ajoute une nouvelle équipe à la base de données factice."""
    f1_teams.append(team)

    
