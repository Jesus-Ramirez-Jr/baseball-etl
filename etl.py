import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date, timedelta
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


def extract(team, load_date):
    loaded_teams = get_loaded_teams(load_date)
    if team in loaded_teams:
        return None
    data = schedule_and_record(2024, team)
    filtered_data = data[data['Date'].str.contains(str(load_date))]
    return filtered_data


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


def load(df_transform, team, load_date, table_name='games'):
    try:
        engine = create_engine(
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")

        with engine.begin() as conn:
            df_transform.to_sql(table_name, con=engine,
                                if_exists='append', index=False)
            conn.execute(text("""
                INSERT INTO audit_log (tm, game_date, loaded_at, status)
                VALUES (:tm, :game_date, NOW(), :status)
                """), {"tm": team, "game_date": load_date, "status": "success"})

            print(
                f"{team} was successfully loaded on {load_date} and logged to audit_table")

    except Exception as e:
        try:
            engine = create_engine(
                f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO audit_log (tm, game_date, loaded_at, status)
                    VALUES (:tm, :game_date, NOW(), :status)
                    """), {"tm": team, "game_date": load_date, "status": "failed"})
        except Exception as log_error:
            print(f"Failed to write audit log: {log_error}")
            raise
        print(f"Loading failed: {e}")
        raise


def update_watermark(load_date):
    try:
        engine = create_engine(
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")

        with engine.begin() as conn:
            query = text("UPDATE watermark SET date = :new_date WHERE id = 1")
            conn.execute(query, {"new_date": load_date})

    except Exception as e:
        print(f"Loading failed: {e}")
        raise


def main():
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']

    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {missing}")

    watermark_date = get_watermark()

    one_day = timedelta(days=1)
    date_to_load = watermark_date + one_day

    for team in TEAMS:
        df = extract(team, date_to_load)
        if df is None or df.empty:
            continue
        df = transform(df)
        load(df, team, date_to_load, table_name='games')

    update_watermark(date_to_load)


if __name__ == '__main__':
    main()
