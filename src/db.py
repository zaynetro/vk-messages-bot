"""
Global db object
"""

import shelve

db = shelve.open('example.db', writeback=True)

def close():
    db.sync()
    db.close()
