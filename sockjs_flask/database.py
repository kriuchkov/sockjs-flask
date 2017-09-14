from pydblite.pydblite import Base


def create_db():
    db = Base('dummy', save_to_file=False)
    db.create('sid', 'channel', 'pid')
    db.create_index('sid')
    db.create_index('channel')
    return db