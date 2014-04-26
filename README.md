CNSync
======

File Synchronizer for CampusNet v0.0.1

## Usage

1. Enter your CampusNet username and password to `cnsync.conf`.
2. Find an absolute path in your drive and set it as `ROOT_FOLDER`.
3. Set an interval in minutes for synchronizer.
4. Start the script `python cnsync.py`

Currently compatible with Python 2.7+

## Features
1. File downloading, if it is on Campusnet, that means it is in your harddrive as well.
2. Flexible intervals, you can set an interval for synchronizing files.

## FAQ

* Used CampusNet REST API, you can find the documentation [here](https://www.campusnet.dtu.dk/data/Documentation/Index.aspx).

## TODO
* Dropbox integration
* Increased API coverage
