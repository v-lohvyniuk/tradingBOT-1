import os
import re
import subprocess


def fetch_db_url_for_local():
    output = subprocess.getoutput("heroku config -a bintradingbot-rsi")
    db_url = re.sub(".*\n.*DATABASE_URL: ", "", output)
    db_url = re.sub("postgres://", "postgresql://", db_url)
    return db_url


try:
    DB_URL = os.environ['DATABASE_URL'].replace("postgres", "postgresql")
except Exception as e:
    DB_URL = fetch_db_url_for_local()

    print("####################################################\n"
          "###  Using fallback configs for PG database.    ####\n"
          "####################################################\n")

