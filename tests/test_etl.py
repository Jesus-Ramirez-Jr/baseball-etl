import pandas as pd
from etl import transform
from datetime import date
import pytest


@pytest.fixture
def sample_df():
    sample_data = [{
        'Date': 'Saturday, Mar 30',
        'Tm': 'NYY',
        'Home_Away': 'Home',
        'Opp': 'HOU',
        'W/L': 'W',
        'R': 5.0,
        'RA': 3.0,
        'Inn': 9.0,
        'W-L': '1-0',
        'Rank': 1.0,
        'GB': '0.5',
        'Win': 'Cole',
        'Loss': 'Brown',
        'Save': None,
        'Time': '2:45',
        'D/N': 'D',
        'Attendance': 42000.0,
        'cLI': 1.0,
        'Streak': 1,
        'Orig. Scheduled': None
    }]
    return pd.DataFrame(sample_data)


def test_column_renaming(sample_df):
    df = transform(sample_df)

    assert list(df.columns) == ['date', 'tm', 'home_away', 'opp',
                                'result', 'r', 'ra', 'inn', 'record', 'ranking', 'gb', 'game_num']


def test_date_convert(sample_df):
    df = transform(sample_df)

    assert df['date'].iloc[0] == date(2024, 3, 30)


def test_game_num1(sample_df):
    df = transform(sample_df)
    assert df['game_num'].iloc[0] == 1


def test_game_num2():

    sample_sf_doubleheader = [{
        'Date': 'Saturday, Mar 30 (2)',
        'Tm': 'NYY',
        'Home_Away': 'Home',
        'Opp': 'HOU',
        'W/L': 'W',
        'R': 5.0,
        'RA': 3.0,
        'Inn': 9.0,
        'W-L': '1-0',
        'Rank': 1.0,
        'GB': '0.5',
        'Win': 'Cole',
        'Loss': 'Brown',
        'Save': None,
        'Time': '2:45',
        'D/N': 'D',
        'Attendance': 42000.0,
        'cLI': 1.0,
        'Streak': 1,
        'Orig. Scheduled': None
    }]

    df = pd.DataFrame(sample_sf_doubleheader)
    df = transform(df)
    assert df['game_num'].iloc[0] == 2
