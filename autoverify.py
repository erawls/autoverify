import argparse
import json
import os
import re
import shutil
from glob import glob
from sys import exit
from typing import List

import requests

import verify

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-c", "--contrib-path", help="input folder (games)")
parser.add_argument(
    "-s", "--stash-path", help="output folder (valid games are moved here)"
)
parser.add_argument("-w", "--webhook-url", help="discord webhook url", required=False)
parser.add_argument(
    "-t",
    "--check-stash",
    action="store_true",
    help="check for games with invalid format",
    required=False,
)
parser.add_argument(
    "-l",
    "--log-failures",
    help="Filepath to save the name of failed validations",
    required=False,
)
parser.add_argument(
    "-k",
    "--keep-files",
    help="Keep files instead of deleting them",
    required=False,
    action="store_true",
)
parser.add_argument(
    "-r",
    "--recurse-directories",
    help="Scan for files in directory and all sub directories recursively",
    required=False,
    action="store_true",
)
args = parser.parse_args()
config = vars(args)

CONTRIB_PATH = config["contrib_path"]
STASH_PATH = config["stash_path"]
DISCORD_WEBHOOK_URL = config["webhook_url"]
CHECK_STASH = config["check_stash"]
LOG_FAILURES = config["log_failures"]
KEEP_FILES = config["keep_files"]
RECURSIVE_SCAN = config["recurse_directories"]


def verify_file_path(file_path: str) -> bool:
    """Make sure the file being targeted is a valid path, or could be a valid path"""

    dirname = os.path.dirname(file_path) or os.getcwd()
    return os.access(dirname, os.W_OK)


def send_hook(message_content):
    """Send notices to discord if configured"""

    if not DISCORD_WEBHOOK_URL:
        return

    try:
        print(message_content)
        payload = {"username": "Contributions", "content": message_content}
        headers = {"Content-type": "application/json"}
        response = requests.post(
            DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers, timeout=10
        )
        response.raise_for_status()
    except IOError as e:
        print(f"Error occured during send_hook! {e}")


def log_errors(invalid_file_path: str):
    """Write verification errors to specifed file"""

    if not LOG_FAILURES:
        return

    if not verify_file_path(LOG_FAILURES):
        raise FileNotFoundError(
            f"Path {LOG_FAILURES} is not in a valid file path format. Please correct and try again"
        )

    try:
        with open(LOG_FAILURES, "a+", encoding="utf-8") as f:
            f.write(f"{invalid_file_path}\n")
    except IOError as e:
        print(f"Error occured during log_errors! {e}")


def get_files(folder_path: str) -> List[str]:
    """Retrieves as list of valid files from the given directory"""

    if not os.path.exists(folder_path):
        return []

    valid_filetypes = (".nsp", ".nsz", ".xci", ".xcz")

    return filter(
        lambda f: any((x in f.lower() for x in valid_filetypes)),
        glob(rf"{folder_path}\*", recursive=bool(RECURSIVE_SCAN)),
    )


def handle_folder():
    """Validate and move file to target, or remove if invalid and not specified otherwise"""

    if not os.path.exists(CONTRIB_PATH):
        os.makedirs(CONTRIB_PATH)
        print(
            f"Please put your game files in: {CONTRIB_PATH} and run this script again."
        )

    for filename in get_files(CONTRIB_PATH):
        try:
            send_hook(f"new file found: {filename}")

            if verify.verify(filename):
                send_hook("Signature valid, moving to stash...")
                stash_dest = os.path.join(STASH_PATH, os.path.basename(filename))
                os.makedirs(stash_dest, exist_ok=True)
                shutil.move(filename, stash_dest)
                send_hook("Done")
            else:
                log_errors(filename)
                if not KEEP_FILES:
                    send_hook("Signature Invalid! deleting...")
                    os.remove(filename)
        except IOError as e:
            print(f"An error occurred: {e} on file {filename}")
            send_hook(f"An error occurred: {e} on file {filename}")
            log_errors(filename)


def check_folder(folder_path: str = CONTRIB_PATH):
    """Verify Naming conventions of files in the folder"""

    if not verify_file_path(folder_path):
        print(f"Path {folder_path} is not a valid path")

    files = get_files(folder_path)

    if not files:
        print("No files of valid type found, exiting")
        exit(0)

    print("Checking for invalid file names...\n")
    for file in files:
        try:
            curr_file = os.path.basename(file)
            send_hook(f"\nnew file found: {curr_file}")

            fields = {
                "titleid": None,
                "version": None,
            }

            send_hook("Checking syntax...")
            res = re.findall(r"\[([A-Za-z0-9_. ]+)\]", curr_file)

            for arg in res:
                if len(arg) == 16:
                    fields["titleid"] = arg
                if arg.upper() in ["BASE", "UPD", "DLC", "UPDATE"]:
                    fields["filetype"] = arg
                if arg.lower().startswith("v") or (arg[:1].isdigit() and len(arg) < 16):
                    fields["version"] = arg

            print(
                f"{curr_file}\nTitleID: {fields['titleid']}\nVersion: {fields['version']}\n {'Filetype: {f}' if (f := fields.get('Filetype')) else ''}"
            )

            if not all(fields.values()):
                send_hook("Syntax invalid! Writing that down...")
                with open("invalid.txt", "a+", encoding="utf-8") as f:
                    if f.tell() != 0:
                        f.write("\n")
                    f.write(
                        f"{curr_file}: MISSING {' and '.join([k.upper() for k,v in fields.items() if not v])}"
                    )
            else:
                send_hook("Syntax valid!")
        except IOError as e:
            send_hook(f"An error occurred: {e}")

    print("Done checking files for invalid names - for list of files check invalid.txt")


if __name__ == "__main__":
    if CONTRIB_PATH and STASH_PATH:
        handle_folder()

    elif CONTRIB_PATH and CHECK_STASH:
        check_folder()

    else:
        parser.print_help()
