# WindBug
Scrape the JSOC web page for wind reports and send an email when they match a criteria.

```
python3 WindBug.py -h
usage: WindBug.py [-h] [--avgspd AVGSPD] [--maxspd MAXSPD] [--nsamples NSAMPLES] [--pollsecs POLLSECS] [--server SERVER] [--user USER]
                  [--password PASSWORD] [--from FROM] [--to TO] [-c]

Monitor wind values that are scraped from the JSOC web page.
If they meet a certain criteria, send an email.

Arguments not specified on the command line are taken from
~/.config/WindBug/WindBug.ini.

Run the program once to create the initial .ini file, (it will give errors),
and then edit ~/.config/WindBug/WindBug.ini.
Or just specifiy all arguments on the command line.

**Be careful of sharing this file, if account/password details are specified there.**

optional arguments:
  -h, --help           show this help message and exit

optional arguments:
  --avgspd AVGSPD      Mean speed(kts) must be below this
  --maxspd MAXSPD      Max speed(kts) must be below this
  --nsamples NSAMPLES  Number of samples to collect
  --pollsecs POLLSECS  Number of seconds between samples
  --server SERVER      SMTP server
  --user USER          SMTP user name
  --password PASSWORD  SMTP user password
  --from FROM          Email from address
  --to TO              Email to address
  -c, --config         Print the configuration and exit
  ```