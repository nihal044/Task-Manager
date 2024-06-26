import databases
import sqlalchemy
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

def get_db() -> Session: # type: ignore
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
