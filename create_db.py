import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

Base = declarative_base()

# Define the User table
users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String, unique=True, index=True),
    Column('password', String),
    Column('role', String)
)

# Define the Task table
tasks = Table(
    'tasks', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('title', String, index=True),
    Column('description', String),
    Column('due_date', DateTime),
    Column('completed', Boolean, default=False),
    Column('user_id', Integer, ForeignKey('users.id'))
)

# Create the tables in the database
metadata.create_all(engine)

print("Database created and tables initialized!")
