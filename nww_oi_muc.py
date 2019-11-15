#!/usr/bin/env python
# encoding: utf-8
'''
gov.noaa.nww_oi.nww_oi_muc -- shortdesc

gov.noaa.nww_oi.nww_oi_muc is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2019 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import yaml
import logging.config
import coloredlogs
import getpass
import threading
import datetime
import numpy as np
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from threading import Timer
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from socket import gethostname
import nww_oi_muc_bot as bot
import nww_oi_rate as rate
from signal import signal, SIGINT
from sys import exit


from optparse import OptionParser


raw_input = input
# Create a custom logger
logger = logging.getLogger(__name__)


__all__ = []
__version__ = 0.1
__date__ = '2019-11-05'
__updated__ = '2019-11-05'

DEBUG = 0
TESTRUN = 0
PROFILE = 0
OI_URL = "nwws-oi.weather.gov"
OI_PORT = 5223

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2019 user_name (organization_name)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"
        
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-l", "--logconfig", dest="logconfig", help="yaml logging config file", default='./logging.yaml')
        parser.add_option('-v', '--verbose', help='set logging to COMM', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO)

        # set defaults
        
        # JID and password options.
        parser.add_option("-j", "--jid", dest="jid", help="JID to use")
        parser.add_option("-p", "--password", dest="password", help="password to use")
        parser.add_option("-r", "--room", dest="room", help="MUC room to join", default='nwws@conference.nwws-oi.weather.gov/nwws-oi')
        parser.add_option("-n", "--nick", dest="nick", help="MUC nickname", default=gethostname())
        parser.add_option("-m", "--metrics", dest="metrics", help="display MUC metrics", action="store_true")

        # process options
        (opts, args) = parser.parse_args()
        
        # Setup logging.
        setup_logging(default_level=opts.loglevel)
        
        logger.info('Started')

        if opts.loglevel > 0:
            logger.info("verbosity level = %d" % opts.loglevel)
            
        if opts.jid is None:
            opts.jid = raw_input("Username: ")
        
        if opts.password is None:
            opts.password = getpass.getpass("Password: ")
        
        if opts.room is None:
            opts.room = raw_input("MUC room: ")
        
        if opts.nick is None:
            opts.nick = raw_input("MUC nickname: ")

        # MAIN BODY #
        logger.debug("Username {}, Password {}".format(opts.jid, opts.password))
        
        if ('@' not in opts.jid):
            opts.jid = "{}@{}".format(opts.jid,'conference.nwws-oi.weather.gov/nwws-oi')
        
        global xmpp
        global metrics
        global sleek_oi
        xmpp = bot.MUCBot(opts.jid, opts.password, opts.room, opts.nick,OI_URL)
        sleek_oi = threading.Thread(target=sleek)
        sleek_oi.start()
        
        if (opts.metrics):
            metrics = rate.OIMetrics_Rate(xmpp)
            global fig
            fig = plt.figure()
            
            global ax
            global ay
            global graph
            global image_timer
        
            image_timer = Timer(500, snapshot, ()).start()
        
            ax = fig.add_subplot(2,1,1) 
            ay = fig.add_subplot(2,1,2)
            graph = animation.FuncAnimation(fig, animate,interval=10000, fargs=(metrics,))
            plt.tight_layout()
            plt.show()

    except Exception as e:
        print (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

def setup_logging(default_path='./logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=logging.DEBUG)
        print('Failed to load configuration file. Using default configs')
  
def animate(x, ani = None):
        # Limit x and y lists to 20 items
        if (ani.avg is not None):
            xs = ani.avg[:100, 0]
            ys = ani.avg[:100, 1]
            zs = ani.avg[:100, 2]
            
            oi_ip_1 = None
            
            # Draw x and y lists
            ax.clear()
            ax.xaxis.set_major_locator(MultipleLocator(int((ani.interval/60)*5)))
            ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
            ax.plot(xs, ys, 'o-')
            start, end = ax.get_xlim()
            #ax.xaxis.set_ticks(np.arange(start, end, (ani.interval/60)*5))
            ax.grid()
            for x in ani.avg:
                if (oi_ip_1 is None):
                    oi_ip_1 = x
                    ax.annotate(oi_ip_1[3],
                                xy=(x[0], x[1]), xycoords='data',
                                xytext=(15, 25), textcoords='offset points',
                                arrowprops=dict(facecolor='black', shrink=0.05),
                                horizontalalignment='left', verticalalignment='bottom')
                elif oi_ip_1[3] != x[3]:
                    ax.annotate(x[3],
                                xy=(x[0], x[1]), xycoords='data',
                                xytext=(15, 25), textcoords='offset points',
                                arrowprops=dict(facecolor='black', shrink=0.05),
                                horizontalalignment='left', verticalalignment='bottom')
                    break;

            # Format plot
            plt.subplot(2,1,1)
            plt.tight_layout(pad=4.0)
            
            plt.title('Average Product Ingest Rate')
            plt.ylabel('Products / {}min'.format(ani.interval/60))
            
            ay.clear()
            ay.xaxis.set_major_locator(MultipleLocator(int((ani.interval/60)*5)))
            ay.xaxis.set_major_formatter(FormatStrFormatter('%d'))
            ay.yaxis.set_major_locator(MultipleLocator(2))
            ay.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
            

            # For the minor ticks, use no labels; default NullFormatter.
            ay.xaxis.set_minor_locator(MultipleLocator(5))
            ay.yaxis.set_minor_locator(MultipleLocator(1))
            
            ay.plot(xs, zs, '*-')
            ay.grid()
            
            plt.subplot(2,1,2)
            plt.tight_layout(pad=4.0)
            #plt.xticks(np.arange(min(xs), max(xs)+1, step=int(ani.interval/60)*5),rotation=45, ha='right')
            plt.title('Presence Count')
            plt.ylabel('Presence / {}min'.format(ani.interval/60))
            
def snapshot():
    timenow = datetime.datetime.now().strftime("%m%d%y-%H%M%S")
    fig.savefig("oi-monitor-{}.png".format(timenow))
    image_timer = Timer(500, snapshot, ()).start()
    
            
def handler(signal_received, frame):
    # Handle any cleanup here
    logging.error('SIGINT or CTRL-C detected. Exiting gracefully')

    try:
        graph = None
        
        if (image_timer is not None):
            if(image_timer.isAlive()):
                image_timer.cancel()
        
        if (xmpp != None):
            xmpp.disconnect(wait=True)
            xmpp = None
        
    except Exception as e:
        logging.warning(e.message)
    finally:
        logging.info("=>>> now exit and close.")
        #sys.exit(-1)
        exit(0)
        
def sleek():
    xmpp['feature_mechanisms'].unencrypted_plain = True
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199', {'keepalive': True, 'interval': 300, 'timeout': 5})  # XMPP Ping


    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect((OI_URL,OI_PORT),use_tls=True, use_ssl=True):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        # 
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        logger.info("Done")
    else:
        logger.error("Unable to connect.")

          
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'gov.noaa.nww_oi.nww_oi_muc_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    signal(SIGINT, handler)
    sys.exit(main())