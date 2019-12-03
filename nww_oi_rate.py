'''
Created on Nov 8, 2019

@author: warrick.moran
'''
import nww_oi_muc_bot as MUCBOT
import datetime
import logging
import socket
import json
import codecs
import numpy as np
from threading import Timer

# Create a custom logger
logger = logging.getLogger(__name__)


class OIMetrics_Rate(object):
    '''
    classdocs
    '''


    def __init__(self, muc: MUCBOT, interval=5):
        '''
        Constructor
        '''
        self.avg = None
        self.muc = muc
        self.interval = interval * 60
        self.start_time = datetime.datetime.now()
        
        self.timer = Timer(self.interval, self.calculate, ())
        self.timer.start()
        self.xs = []
        self.ys = []
    
    def calculate(self):
        timenow = datetime.datetime.now()
        timediff = (timenow - self.start_time)
        timediff_min = int(timediff.seconds / 60)
        average = self.muc.product_count / timediff_min
        
        logger.debug("Rate Calculate: Member List-{}, TimeDiff-{}, TimeDiff Min-{}, Avg-{}".format(len(self.muc.member_list),timediff, timediff_min, average))
    
        if (self.avg is None):
            self.avg = np.array([[timediff_min,average,len(self.muc.member_list),socket.gethostbyname(self.muc.url),timenow]])
        else:
            self.avg = np.append(self.avg, [[timediff_min,average, len(self.muc.member_list),socket.gethostbyname(self.muc.url), timenow]],axis=0)
        
        self.store()
        self.reset()
            
    def reset(self):
        if (self.timer.isAlive()):
            self.timer.cancel()
        self.timer = Timer(self.interval, self.calculate, ())
        self.timer.start()
        
    def start(self):
        self.reset()
        self.init()
        self.timer.start()
        
    def init(self):
        if (self.avg is not None):
            del self.avg
            self.avg = None
            
    def store(self):
        if (self.avg is not None):
            if (self.avg.shape[0] >= 5):
                with open("presence.json", "w") as jsonFile:
                    json.dump(self.avg.tolist(), jsonFile, separators=(',', ':'), sort_keys=True, indent=4)### this saves the array in .json format
                #header = "time, presence, server-ip"
                #np.savetxt('presence-{}.dat'.format(datetime.datetime.now().strftime("%m%d%y-%H%M%S")), self.avg, header=header)
                self.init() 
                
        