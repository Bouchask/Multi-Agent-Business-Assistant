import os
from sqlalchemy import create_engine
from backend.app.config.settings import settings

# Ensure sqlite data directory exists if using sqlite
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    db_file_path = db_url.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(os.path.abspath(db_file_path)), exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=(settings.APP_ENV == "development" and settings.LOG_LEVEL.upper() == "DEBUG")
)
