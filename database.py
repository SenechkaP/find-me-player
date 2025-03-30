from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from env_values import db_username, db_password, db_host, db_port, db_name

DATABASE_URL = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
