import os

try:
    DB_URL = os.environ['DATABASE_URL'].replace("postgres", "postgresql")
except Exception as e:
    DB_URL = "postgresql://ajrduocxletvlv:20c1c4981cba66df703efd82959a45938665988f3262dd073090852134db4750@ec2-63-32-248-14.eu-west-1.compute.amazonaws.com:5432/dstlhpucamj4"
    print("####################################################\n"
          "###  Using fallback configs for PG database.    ####\n"
          "###  Please pay attention they may be outdated. ####\n"
          "###  For new creds visit the following url:     ####\n"
          "####################################################\n"
          "https://data.heroku.com/datastores/8eddbae0-1de4-4951-89b8-56000091939a#administration ")

DB_PORT = "5432"
DB_NAME = "dstlhpucamj4"
DB_USER = "ajrduocxletvlv"
DB_PASSWORD = "20c1c4981cba66df703efd82959a45938665988f3262dd073090852134db4750"
