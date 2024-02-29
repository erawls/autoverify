# AutoVerify
Original work by @themoonisacheese.

Auto verify NSP, NSZ, XCI, XCZ to check if they have a valid hash and signature, on Linux and Windows.

Verification code stolen from NSCB, with mods from @seiya-git.
This is essentially a stripped down squirrel.py that does only verification, meant for batch processing of stashes.

This fork is to be an enhanced version - with minor cleanups on touched files and features added while being open to the community to contribute as they see fit.


# Usage

```
usage: autoverify.py [-h] [-c CONTRIB_PATH] [-s STASH_PATH] [-w WEBHOOK_URL] [-t] [-l LOG_FAILURES] [-k KEEP_FILES] [-r RECURSE_DIRECTORIES]

options:
  -h, --help            show this help message and exit
  -c CONTRIB_PATH, --contrib-path CONTRIB_PATH
                        input folder (games) (default: None)
  -s STASH_PATH, --stash-path STASH_PATH
                        output folder (valid games are moved here) (default: None)
  -w WEBHOOK_URL, --webhook-url WEBHOOK_URL
                        discord webhook url (default: None)
  -t, --check-stash     check for games with invalid format (default: False)
  -l LOG_FAILURES, --log-failures LOG_FAILURES
                        Filepath to save the name of failed validations (default: None)
  -k KEEP_FILES, --keep-files KEEP_FILES
                        Keep files instead of deleting them (default: None)
  -r RECURSE_DIRECTORIES, --recurse-directories RECURSE_DIRECTORIES
                        Scan for files in directory and all sub directories recursively (default: None)
```
# Installation
1) clone this repo
2) cd into new "autoverify" directory
3) run "python -m venv venv" [without quotes]
4) Activate the new venv by running the following in a terminal/command window:
  a) Windows: .venv\Scripts\activate.bat
  b) Linux:   source .venv/bin/activate
5) Install requirements by running the following command in the same window from step 4: "pip install -r requirements" [without quotes]
6) Place a copy of your (legally acquired) prod.keys in the same directory as autoverify.py, and then rename "prod.keys" to "keys.txt" [again, without quotes]
7) When using the program, ensure to open a command window and activate the venv following the instructions in step 4, or using the "python" executable found in the venv's folder itself.

# Examples
```
1) Check games in "/path/to/unverified/games" and move all valid ones to the target directory "/path/to/stash"
  * python autoverify.py -c /path/to/unverified/games -s /path/to/stash

2) Same as example one, but scan all subfolders found in "/path/to/unverified/games". NOTE: Output will be flattend in destination
  * python autoverify.py -c /path/to/unverified/games -s /path/to/stash -r

3) Same as example two, but keep the invalid files instead of deleting them
  * python autoverify.py -c /path/to/unverified/games -s /path/to/stash -r -k
```

If the stash (destination) folder does not exist, it will attempt to be created.

Files that do not pass the signature verification will be **PERMANENTLY DELETED** unless the -k or --keep-files flag is passed. Due to the logic in retrieving the files list it *should" only target Switch ROM files (".nsp", ".nsz", ".xci", ".xcz"), but discretion is advised.
