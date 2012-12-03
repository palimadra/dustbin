#!./env/bin/python

import spyglass.db.orm as orm
orm.Base.metadata.drop_all(orm.engine)
