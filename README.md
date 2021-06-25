# radius-logs-parser

The script is designed for parsing log files, collecting, analyzing and storing data from these logs.

Simple script call:

python -u search.py

Calling data to a sqlite database file.

python -u search.py -S

python -u search.py --save

Call with the indication of the path to the log file or folder with log files.
path to single file "sample.log"

python -u search.py -P logs/sample.log

python -u search.py --path logs/sample.log

path to directory with log files "sample_directory"
python -u search.py -P logs/sample_directory

python -u search.py --path logs/sample_directory

Call with data output on the screen.

python -u search.py -V

python -u search.py --verbose

With limited output lines.

python -u search.py -V -L 10

python -u search.py --verbose --limit 10

