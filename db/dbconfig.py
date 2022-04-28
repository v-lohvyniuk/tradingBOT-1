import os

DB_URL = os.environ['DATABASE_URL'].replace("postgres", "postgresql")
print("Here are my creds la la la " + DB_URL)
# DB_URL = "postgresql://ajrduocxletvlv:20c1c4981cba66df703efd82959a45938665988f3262dd073090852134db4750@ec2-63-32-248-14.eu-west-1.compute.amazonaws.com:5432/dstlhpucamj4"
DB_PORT = "5432"
DB_NAME = "dstlhpucamj4"
DB_USER = "ajrduocxletvlv"
DB_PASSWORD = "20c1c4981cba66df703efd82959a45938665988f3262dd073090852134db4750"
