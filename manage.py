from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from exchangeogram import app, db
from config import Config

app.config.from_object(Config)

migrate = Migrate(app, db)
manager = Manager(app)

@MigrateCommand.command
def create():
    db.create_all()

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()