from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'postgresql://postgres:jag88@localhost:5432/ExpenseTracker'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(auto_commit = False, autoflush=False, bind=engine)

Base = declarative_base()
