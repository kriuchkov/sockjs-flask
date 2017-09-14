from pydblite.pydblite import Base


def create_db():
    db = Base('dummy', save_to_file=False)
    db.create('sjid', 'chan', 'pid')
    db.create_index('sjid')
    db.create_index('chan')
    #n = 100
    #for i in range(n):
    #    for j in range(100 * n):
    #        db.insert(sjid='aidf{}js'.format(j), chan='fsdf{}rys'.format(i))
    return db