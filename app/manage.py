"""Module for database migrations"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from control import APP, DB

MIGRATE = Migrate(APP, DB)
MANAGER = Manager(APP)

MANAGER.add_command('DB', MigrateCommand)

if __name__ == '__main__':
    MANAGER.run()
