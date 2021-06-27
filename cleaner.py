"""Main file to run the program"""

from argparse import ArgumentParser
from datetime import date
from os import chdir, path
from time import sleep

from application import gui_application, cmd_application, cleaner
from db import init_db

# Set current did
chdir(path.abspath(path.dirname(__file__)))

parser = ArgumentParser(description="Cleanup files in directory. Cleaner runs once a new day and sends file to Trash")
parser.add_argument("--cmd", action="store_true", help="Run the cmd application to add, view or delete directories")
parser.add_argument("--gui", action="store_true", help="Run the gui application to add, view or delete directories")
args = parser.parse_args()

init_db()

if args.gui:
    gui_application()
elif args.cmd:
    cmd_application()
else:
    last_run = None
    while True:
        if date.today() != last_run:
            cleaner()
            last_run = date.today()
        sleep(3600)
