#  Pybaseball → MySQL ETL Pipeline

A  Python script that extracts data from a baseball python package use for data analysis, transforms it with pandas, and loads it into a MySQL database. Built to understand the ETL process using incremental sync and watermark techniques.

---

## Why This Exists

ETL processes have various sync methods. This project was built to:

- Understand how and why a incremental load is implemented.
- Have an understanding of watermark techniques used for incremental loading.

---

## How It Works

The script follows the following ETL flow:

1. **Get Watermark** — Retrieves current watermark date
2. **Load Teams** — Loads  teams for a from python package
3. **Extract** — Filters for teams with a specific watermark date
4. **Transform** — Cleans and structures the data using `pandas`
5. **Load** - Writes the result to a local MySQL database via `SQLAlchemy`
6. **Update Watermark** - Add one day to the current watermark date

Error handling is implemented at each stage so failures are easy to isolate and debug.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core scripting language |
| pybaseball | Baseball package with season info |
| pandas | Data transformation |
| SQLAlchemy | Database connection and ORM |
| MySQL | Target database |
| Datetime| methods to work with dates |

---

## Setup & Usage

### Prerequisites

- Python 3.x
- A MySQL instance running locally (or update the connection string for remote)

### Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd <repo-folder>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt


# 4. Set environment variables
export DB_USER=your_mysql_username
export DB_PASSWORD=your_mysql_password

# 5. Run the script
python etl.py
```



---



### How to run

- `.env` — Your local copy with real credentials. **Never commit this file.** Make sure it's in `.gitignore`.


```bash
export DB_USER=your_actual_username
export DB_PASSWORD=your_actual_password
export DB_NAME=your_actual_db_name
python etl.py
```


---

## Key Concepts Covered

- **Watermark Tracking** - A technique used for incremental loading. A watermark date is necessary for script to start loading correct info so no duplicates are created.
- **Incremental Loading** - A new etl sync mode used to load newly added records since the previous sync
- **Audit Logging** - Logged successes and failures to for troubleshooting and root analysis purposes.
- **Doubleheader Handling** - Necessary step to handle when teams play multiple games in the same day.
- **Pybaseball** -  A baseball package used for data analysis. A new data source to pull from.


---

## Schema

- **Games** -  Table of games store information on results of games. Each day's result is appended. Primary key is (tm, date, game_num) to handle doubleheaders.
- **watermark** - Table with a single date to act as a checkpoint to track the most recent processed data. Primary key is id.
- **audit_log** - Table that logs each success of failure for each team. provides a step-step history of data movement. Primary key is (tm, date).