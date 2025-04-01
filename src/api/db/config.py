from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
DB_TIMEZONE=os.getenv("DB_TIMEZONE")