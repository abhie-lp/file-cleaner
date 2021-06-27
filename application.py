"""Python file for terminal and yui applications"""

from contextlib import closing
from datetime import datetime
from glob import glob
from os import path, system
from re import compile, match
from sys import platform

from db import get_db

if platform == "linux":
    # For linux send files to trash using 'gio trash' command
    delete = "gio trash '%s'"
else:
    # Using CmdUtils (http://www.maddogsw.com/cmdutils/) for Windows.
    delete = "Recycle.exe %s"


def gui_application():
    """Function to run the gui application of program"""
    print("Work in progress")


def tprint(indent: int, message: str, *args) -> None:
    """Print in terminal with correct whitespace before message"""
    print(" " * indent + message, *args)


def tinput(indent: int, message: str) -> str:
    """Take input from terminal with correct whitespace before message"""
    return input(" " * indent + message)


def cmd_application():
    """Run the terminal apploication"""
    while True:
        try:
            print("[add] - Add new directory\n"
                  "[all] - Get all added directories\n"
                  "[del] - Remove one or more directories\n"
                  "[q]   - Exit")
            option = tinput(0, "[>] ").lower()

            if option == "add":
                while True:
                    tprint(2, "[*] Enter the absolute path of directory or type 'back' to go back")
                    dir_path = tinput(2, "[>] ").strip()
                    if dir_path == "back":
                        break
                    elif not path.isabs(dir_path):
                        tprint(2, "[-] Entered path is not absolute")
                    elif not path.exists(dir_path):
                        tprint(2, "[-] Entered path does not exist")
                    elif not path.isdir(dir_path):
                        tprint(2, "[-] Entered path is not a directory")
                    else:
                        # Remove trailing forward slash if present
                        dir_path = path.normpath(dir_path)

                        # Used closing to auto close db after code comes outside with
                        with closing(get_db()) as db, db:
                            if db.execute("SELECT path FROM directories WHERE path = ?", (dir_path,)).fetchone():
                                tprint(2, "[-] Entered directory already exists")
                                continue

                        tprint(4, "[*] Enter file types separated by whitespace and without dot or"
                                  " 'all' for all file types")
                        extensions: list = tinput(4, "[>] ").replace(".", " ").replace(",", " ").strip().split(" ")
                        if extensions[0] == "all":
                            extensions: str = "all"
                        else:
                            extensions: str = ";".join(extensions)

                        tprint(4, "[*] Enter number of days after which file is to be deleted.")
                        interval = int(tinput(4, "[>] ").strip())
                        with closing(get_db()) as db, db:
                            db.execute(
                                "INSERT INTO directories (path, file_types, interval) VALUES (?, ?, ?)",
                                (dir_path, extensions, interval)
                            )
                            tprint(4, f"[*] New entry for {dir_path}")
                        break
            elif option == "all":
                print()
                tprint(2, f"{'ID':<3} {'Path':<60} {'File Types':<30} Interval(days)")

                with closing(get_db()) as db, db:
                    for ind, row in enumerate(db.execute("SELECT * FROM directories ORDER BY path")):
                        tprint(2, f"{ind:<3} {row['path'][:59]:<60} {row['file_types'][:29]:<30} {row['interval']}")
                    print()
            elif option == "del":
                while True:
                    print()
                    tprint(2, f"{'ID':<3} {'Path':<60} {'File Types':<30} Interval(days)")
                    with closing(get_db()) as db, db:
                        rows = db.execute("SELECT * FROM directories ORDER BY path").fetchall()
                    for ind, row in enumerate(rows):
                        tprint(2, f"{ind:<3} {row['path'][:59]:<60} {row['file_types'][:29]:<30} {row['interval']}")
                    print()

                    tprint(2, "[*] Enter one or more IDs separated by whitespace to delete entry or "
                              "'back' to go back")
                    ids: list = input(" " * 2 + "[>] ").strip().split()
                    if ids[0] == "back":
                        break
                    with closing(get_db()) as db, db:
                        for i in ids:
                            i = int(i)
                            tprint(4, f"[*] Deleting entry {rows[i]['path']}")
                            db.execute("DELETE FROM directories WHERE id = ?", (rows[i]["id"],))
                            db.commit()
                            tprint(4, f"[*] Deleted entry {rows[i]['path']}")
            elif option == "q":
                tprint(0, "Bye bye..!!!")
                break
        except KeyboardInterrupt:
            tprint(0, "[>] Exiting the program")
            break
        except Exception as e:
            tprint(0, "[-] Some error:", e)


def cleaner():
    """Program to remove files"""
    today = datetime.today().date()
    with closing(get_db()) as db, db:
        for row in db.execute("SELECT * FROM directories").fetchall():
            tprint(0, "[*] Checking directory", row["path"])
            if not row["file_types"] == "all":
                pattern = compile(r".*\.(" + r"|".join(row["file_types"].split(";")) + r")$")

            for file in glob(path.join(row["path"], "*")):
                if not path.isfile(file):
                    continue
                if row["file_types"] != "all" and not match(pattern, file):
                    continue
                if (today - datetime.fromtimestamp(path.getmtime(file)).date()).days > row["interval"]:
                    tprint(2, f"[*] Deleting {file}")
                    status = system(delete % file)
                    if status == 0:
                        tprint(2, f"[*] Deleted {file}")
                    else:
                        tprint(2, f"[-] Error in deleting {file}")
