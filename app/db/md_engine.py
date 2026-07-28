from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = (
    os.getenv("TEST_DATABASE_URI")
    if os.getenv("CONFIG_TYPE") == "app.config.TestingConfig"
    else os.getenv("DATABASE_URI")
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_engine(database_uri):
    engine = create_engine(database_uri, echo=True)
    SessionLocal.configure(bind=engine)
    SessionLocal.configure(bind=engine)
    print("ENGINE =", engine.url)
    return engine

# database_uri = (
#     os.getenv("TEST_DATABASE_URI")
#     if os.getenv("CONFIG_TYPE") == "app.config.TestingConfig"
#     else os.getenv("DATABASE_URI")
# )
#
# engine = create_engine(
#     database_uri,
#     echo=True
# )
# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False,
#     expire_on_commit = False
# )
# print("CONFIG_TYPE =", os.getenv("CONFIG_TYPE"))
# print("ENGINE =", engine.url)