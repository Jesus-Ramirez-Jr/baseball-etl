import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date
from pybaseball import schedule_and_record
import pandas as pd

load_dotenv()

TEAMS = [
    'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
    'HOU', 'KCR', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
    'PHI', 'PIT', 'SDP', 'SFG', 'SEA', 'STL', 'TBR', 'TEX', 'TOR', 'WSN'
]


def get_watermark():

    try:
        engine = create_engine(
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")

        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT date FROM watermark WHERE id = 1"))
            row = result.fetchone()
            if row:
                return row[0]
            else:
                return date(2024, 3, 28)

    except Exception as e:
        print(f"Database error: {e}. Falling back to default date.")
        return date(2024, 3, 28)


def get_loaded_teams(load_date):

    try:
        engine = create_engine(
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT tm FROM audit_log WHERE game_date = :load_date AND status = 'success'"), {
                                  "load_date": load_date})
            rows = result.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        print(f"Error: {e}")
        return []


def extract(load_date):
    loaded_teams = get_loaded_teams(load_date)
    results = []

    for team in TEAMS:
        # If team is in the loaded_teams, skip it
        if team in loaded_teams:
            continue
        else:
            data = schedule_and_record(2024, team)
            filtered_data = data[data['Date'].str.contains(str(load_date))]
            results.append(filtered_data)
    return pd.concat(results, ignore_index=True)


def transform(results):
    column_mapping = {
        'Date': 'date',
        'Tm': 'tm',
        'Home_Away': 'home_away',
        'Opp': 'opp',
        'W/L': 'result',
        'R': 'r',
        'RA': 'ra',
        'Inn': 'inn',
        'W-L': 'record',
        'Rank': 'ranking',
        'GB': 'gb'
    }

    df_transform = results.rename(columns=column_mapping)

    destination_columns = ['date', 'tm', 'home_away', 'opp',
                           'result', 'r', 'ra', 'inn', 'record', 'ranking', 'gb']

    df_transform = df_transform[destination_columns]

    return df_transform
