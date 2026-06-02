import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import date

load_dotenv()


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

    skip_teams = []

    try:
        engine = create_engine(
            f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@localhost/{os.environ.get('DB_NAME')}")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT tm FROM audit_log WHERE game_date = :load_date AND status = 'success'"), {
                                  "load_date": load_date})
            if result:
                skip_teams.append(result)
                return skip_teams
            else:
                rows = result.fetchall()
                return rows
    except Exception as e:
        print(f"Error: {e}")
