# pip install python-decouple
from decouple import config as decouple_config


DATABASE_URL = decouple_config("DATABASE_URL", default="")
DB_TIMEZONE = decouple_config("DB_TIMEZONE", default="UTC")