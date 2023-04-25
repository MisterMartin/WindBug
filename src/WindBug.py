import time
import signal
import sys
import pprint
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from ConfigIni import ConfigIni
from WindScrapper import WindScraper
from Mailer import Mailer

class WindBug:
    '''Combines a WindScraper and a Mailer as an alerting system'''

    def __init__(self)->None:
        self.args = self.parseArgs(appName='WindBug')

        self.scraper = WindScraper(samplesToAvg=self.args['nsamples'], pollingSecs=self.args['pollsecs'], avgSpdBelow=self.args['avgspd'], maxSpdBelow=self.args['maxspd'])
        self.mailer = Mailer(server=self.args['server'], user=self.args['user'], fromAddr=self.args['from'], pw=self.args['password'])
        signal.signal(signal.SIGINT, self.sigint)

    def main(self):
        self.scraper.start()
        while True:
            time.sleep(1)
            # alert will be True if an alert is called for.
            # current != None if there has been a new reading since the last call
            alert, current = self.scraper.status()
            if current:
                print('*'+current if alert else ' '+current)
                if alert:
                    self.mailer.sendMail(toAddr=self.args['to'], msg=current)

    def parseArgs(self, appName:str) -> (dict, str):
        '''Get configuration from the ini file and the command line arguments.'''

        defaults = {
            "Main" : {
                "AvgSpdBelow" : '6.0',
                "MaxSpdBelow" : '10.0',
                "SmtpServer" : "smtp.gmail.com",
                "SmtpUser" : "smtp_user_name",
                "SmtpPassword": "hidden",
                "FromEmail" : 'from_email',
                "ToEmail" : 'to_email',
                "Nsamples": '60',
                "PollingIntSecs" : '60',
            }
        }
        config = ConfigIni(appName=appName, defaults=defaults)
        config.save()

        description = f'''
Moniter wind values that are scraped from the JSOC web page.
If they meet a certain criteria, send an email.

Arguments not specified on the command line are taken from
{config.configPath()}.

Run the program once to create the initial .ini file, (it will give errors),
and then edit {config.configPath()}.
Or just specifiy allm arguments on the command line.

**Be careful of sharing this file, if account/password details are specified there.**
'''

        parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
        optional = parser.add_argument_group('optional arguments')
        optional.add_argument('--avgspd', help='Mean speed(kts) must be below this', action='store', default=config.values()['Main']['AvgSpdBelow'])
        optional.add_argument('--maxspd', help='Max speed(kts) must be below this', action='store', default=config.values()['Main']['MaxSpdBelow'])
        optional.add_argument('--nsamples', help='Number of samples to collect', action='store', default=config.values()['Main']['Nsamples'])
        optional.add_argument('--pollsecs', help='Number of seconds between samples', action='store', default=config.values()['Main']['PollingIntSecs'])
        optional.add_argument('--server', help='SMTP server', action='store', default=config.values()['Main']['SmtpServer'])
        optional.add_argument('--user', help='SMTP user name', action='store', default=config.values()['Main']['SmtpUser'])
        optional.add_argument('--password', help='SMTP user password', action='store', default=config.values()['Main']['SmtpPassword'])
        optional.add_argument('--from', help='Email from address', action='store', default=config.values()['Main']['FromEmail'])
        optional.add_argument('--to', help='Email to address', action='store', default=config.values()['Main']['ToEmail'])
        optional.add_argument('-c', '--config', help='Print the configuration and exit', action='store_true', default=False)
        args = parser.parse_args()

        # Convert args to a dictionary
        argsDict = vars(args)
        argsDict['avgspd'] = float(args.avgspd)
        argsDict['maxspd'] = float(args.maxspd)
        argsDict['nsamples'] = int(args.nsamples)
        argsDict['pollsecs'] = int(args.pollsecs)

        if args.config:
            pprint.PrettyPrinter(indent=4).pprint(argsDict)
            sys.exit(0)

        return argsDict

    def sigint(self, a, b):
        self.scraper.terminate()
        sys.exit(0)

if __name__ == '__main__':
    wb = WindBug()
    wb.main()
