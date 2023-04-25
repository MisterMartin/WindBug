from threading import Thread
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time
import smtplib
import re
import requests
requests.packages.urllib3.disable_warnings()
import signal
import sys
from ConfigIni import ConfigIni

class WindScraper(Thread):
    '''Monitor wind conditons scrapped from the McMurdo JSOC wind page

    This is run as a thread. Query it by calling status() periodically to find
    out what the current conditions are, and if the criteria have been met for an alert. 
    The criteria are specified in the constructor.

    The thread is initiated by calling WindScraper.start(). This in turn
    will invoke the WindScrapper.run() method. The thread is terminated
    by calling terminate()
    '''
    def __init__(self, 
            pollingSecs:int=60, 
            samplesToAvg:int=10, 
            avgSpdBelow:float=6.0, 
            maxSpdBelow:float=10.0)->None:
        '''Set the operating criteria for polling and alerting

        Parameters
        ----------
        pollingSecs:int How often to get a sample from the web server.
        samplesToAvg:int How many samples to average over to meet the allert criteria.
        avgSpdBelow:float The mean speed must be below this value to generate an alert.
        maxSpdBelow:float The max speed must be below this value to gernerate an alert.
        '''
        Thread.__init__(self)
        self.pollingSecs = pollingSecs
        self.current = None
        self.alert = False
        self.avgSpdBelow = avgSpdBelow
        self.maxSpdBelow = maxSpdBelow
        self.samplesToAvg = samplesToAvg
        # Set True to signal the thread to exit.
        self.exit = False

    def status(self)->str:
        '''Return the current status as a tuple: (alert:bool, current:str)

        alert: set True if an alert should be sent. It is set to false
               whenever this function is called.
        current: the current conditions, in text form. Set to None
               whenever this function is called, and set to a value when 
               new current conditions are avaiable.
        '''
        retval = (self.alert, self.current)
        self.current = None
        self.alert = False
        return retval

    def run(self):
        '''Loop over scrapes of the web site

        Current conditions and alert status are obtained by calling WindScrapper.status()

        The alert flag is cleared after each call to status().
        '''

        # Keep a running collection od recent wind speeds in wind_speed[]
        wind_speed = []
        # A countdown counter that holds off allerting for the sample span after the last alert.
        holdOff = 0

        while True:
            raw_html = self.simple_get('https://www.mcmurdo.usap.gov/dynamic/weatherlink/b189/images/details.htm')
            if(len(raw_html)) > 12000:
                html = BeautifulSoup(raw_html, 'html.parser')
                lines = html.prettify().split('\n')
                lines_with_kts =  [s for s in lines if 'kts' in s]
                speed = float(''.join(re.findall("\d+\.\d+", lines_with_kts[0])))
                wind_speed.append(speed)
            
            if (len(wind_speed)):
                max_wind = max(wind_speed)
                min_wind = min(wind_speed)
                mean_wind = sum(wind_speed)/len(wind_speed)
                holdOff -= 1

                spanInMins = len(wind_speed)*self.pollingSecs/60.0
                self.current = f'Current:{speed:.1f}  Max:{max_wind:.1f}  Mean:{mean_wind:.1f} in last {spanInMins:.1f} minutes at {time.strftime("%H:%M:%S")} (spd in kts)'

                if (
                    mean_wind < self.avgSpdBelow and 
                    max_wind < self.maxSpdBelow and 
                    len(wind_speed) >= self.samplesToAvg and
                    holdOff <= 0): 
                    self.alert = True
                    holdOff = self.samplesToAvg

                if len(wind_speed) == self.samplesToAvg:
                    # Make room for the next sample
                    wind_speed.pop(0)

            for i in range(self.pollingSecs):
                time.sleep(1)
                if self.exit:
                    return

    def terminate(self):
        self.exit = True

    def simple_get(self, url):
        try:
            with closing(get(url, stream=True, verify=False)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None
        except:
            return None

    def is_good_response(self, resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('html') > -1)

