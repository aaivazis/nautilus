"""
    This module defines a small singleton that runs various scripts in the
    context of the service.
"""

# external imports
from flask.ext.script import Manager

class ServiceManager:

    def __init__(self, service):
        # create and attach a command manager for the service
        self.commandManager = Manager(service.app)

        self.command.add_command('test', )

        @self.commandManager.command
        def syncdb():
            """ Create the database entries. """
            # import the db module
            from nautilus import db
            # create all of the tables
            db.create_all()
            # notify the user
            print("Successfully created database entries.")

        @self.commandManager.command
        def runserver(port = 8000, debug = False, secretKey = 'supersecret'):
            """ Start the service. """
            service.run(int(port), debug, secretKey)

    def run(self):
        """ run the command manager """
        self.commandManager.run()