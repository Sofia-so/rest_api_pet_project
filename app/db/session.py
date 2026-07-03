from app.db.md_engine import SessionLocal
from flask import g

def get_db():
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


def close_db(e):
    db = g.pop("db", None)
    if db is not None:
        db.close()