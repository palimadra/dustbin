#!./env/bin/python

import spyglass.config as config
import spyglass.db.orm as orm

orm.Base.metadata.create_all(orm.engine)


