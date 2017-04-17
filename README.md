# [redacted]-bus-data

Exctract the [redacted] bus schedule from the schedule on the locked Google sheet.

The general idea is to intercept certain AJAX calls made by the Google Docs client,
and use them to reconstruct the schedule.
This was challenging because the format for those AJAX responeses is pretty opaque, and also compressed.
This repository also includes the code I used for reversing the relevant bits of that format.

## Usage

First, fire up [mitmproxy](https://mitmproxy.org/):

```
$ mitmproxy -s mitm.py
```

Point your browser to it as an HTTPS proxy (see [here](http://docs.mitmproxy.org/en/latest/certinstall.html) for dealing with certs),
and navigate to the [redacted] Google sheet.
Click on and wait for each tab, so that all relevant AJAX calls are mada.
The `mitm.py` script should have pulled all of the useful reponses into a directory matching `data-[0-9]*` (the numbers are a timestamp).
Make sure that directory has the following structure:

```
$ ls data-*
fetchrows # directory
edit # html
$ ls data-*/fetchrows
1492317815866 # a bunch of json-like files named with timestamps
1492318234395
...
```

Now, create a file containing a list of tab names (one per line) in the sheet that contain schedules (I will assume you've called it `tabs.txt`).
These are not included in the repository because they would reveal what the document was for.
Finally, use `main.py` to convert the raw AJAX calls to either JSON or KML:

```
$ python3 main.py -h
usage: main.py [-h]
               (--tab-file TAB_FILE | --tab-list [TAB_NAME [TAB_NAME ...]])
               DATA_DIR {json,kml,tsv}

Scrape downloaded AJAX data for the bus schedule

positional arguments:
  DATA_DIR              Path of AJAX data (probably matching "data-[0-9]+")
  {json,kml,tsv}        Output format

optional arguments:
  -h, --help            show this help message and exit
  --tab-file TAB_FILE, -f TAB_FILE
                        File containing list of names of tabs with schedules
                        in them
  --tab-list [TAB_NAME [TAB_NAME ...]], -l [TAB_NAME [TAB_NAME ...]]
                        List of names of tabs with schedules in them
```

For example, the following will output JSON with very similar structure to the original Google sheet:
```
$ python3 main.py data-* json -f tabs.txt
```
KML and TSV files can be uploaded to Google Maps, but this particular data set has too many features,
and so Maps will not accept all of them.
A work around is to create KML or TSV files for subsets of the tabs.
For example, the following creates a KML file just for the bus stop on Saturn:
```
$ python3 main.py data-* kml -l Saturn
```
