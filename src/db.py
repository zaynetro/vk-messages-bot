"""
Global db object
"""

import shelve

db = shelve.open('example.db', writeback=True)

def set(key, value):
    try:
        db[key] = value

    except ValueError:
        pass

def get(key):
    try:
        return db[key]

    except ValueError:
        return None

def dict():
    return db

def sync():
    try:
        db.sync()

    except ValueError:
        pass

def close():
    db.sync()
    db.close()
