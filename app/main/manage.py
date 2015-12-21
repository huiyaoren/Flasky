#!/usr/bin/env python
import os

from app import creat_app, db
from app.models import User, Role

from flask.ext.script import Manager, Shell
from falsk.ext.migrate import Migrate, MigrateCommand


app = creat_app(os.getenv('FLAK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
	"""run the unit tests"""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosit=2).run(tests)


if __name__ == '__main__':
	manager.run()