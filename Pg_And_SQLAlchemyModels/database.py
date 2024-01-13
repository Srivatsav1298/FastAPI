from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/hostname>/<database_name>"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Ronick58@localhost/fastapi"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# Below engine is responsible for SQLAlchemy to connect to Postgres
engine = create_engine(SQLALCHEMY_DATABASE_URL)
#To talk to a database we need to create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Creates a session to our database for to communicate
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()