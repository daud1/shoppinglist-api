from flask_migrate import MigrateCommand
from app import mgr, migr, db

mgr.add_command('db', MigrateCommand)

if __name__ == '__main__':
    mgr.run()
