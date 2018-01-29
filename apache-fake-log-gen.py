#!/usr/bin/python
import time
import datetime
import pytz
import numpy
import random
import gzip
import zipfile
import sys
import argparse
from faker import Faker
from random import randrange
from tzlocal import get_localzone
local = get_localzone()

#todo:
# allow writing different patterns (Common Log, Apache Error log etc)
# log rotation


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT", choices=['LOG','GZ','CONSOLE'] )
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int, default=1)
parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)

args = parser.parse_args()

log_lines = args.num_lines
file_prefix = args.file_prefix
output_type = args.output_type

faker = Faker()

timestr = time.strftime("%Y%m%d-%H%M%S")
otime = datetime.datetime.now()

#For my Requirement change the timestr in the outputFileName when file prefix is used
outFileName = 'access_log_'+timestr+'.log' if not file_prefix else file_prefix+'.log'

#outFileName = 'access_log_'+timestr+'.log' if not file_prefix else file_prefix+'_access_log_'+timestr+'.log'


for case in switch(output_type):
	if case('LOG'):
		f = open(outFileName,'w')
		break
	if case('GZ'):
		f = gzip.open(outFileName+'.gz','w')
		break
	if case('CONSOLE'): pass
	if case():
		f = sys.stdout

sourceIp=["186.46.191.148","115.46.129.238","102.39.148.153","75.9.244.161",
"103.76.174.122","114.255.6.234","133.7.53.26","246.62.135.218","235.132.165.195", 
"145.128.91.110", "187.140.80.153", "164.157.18.87", "57.199.13.22", 
"83.207.72.1", "8.145.66.245"]
response=["200","201","204","400","401","403","404","500","503"]

verb=["GET","POST","DELETE","PUT","HEAD"]

resources=["/list","/wp-content","/wp-admin","/explore","/search/tag/list","/app/main/posts","/posts/posts/explore","/apps/cart.jsp?appID="]

ualist = [faker.firefox, faker.chrome, faker.safari, faker.internet_explorer, faker.opera]

flag = True
while (flag):
	if args.sleep:
		increment = datetime.timedelta(seconds=args.sleep)
	else:
		increment = datetime.timedelta(seconds=1)
	otime += increment * 0.001

	ip = random.choice(sourceIp) #
	dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
	tz = datetime.datetime.now(local).strftime('%z')
	vrb = numpy.random.choice(verb,p=[0.5,0.1,0.1,0.2,0.1]) #Probability for word

	uri = random.choice(resources)
	if uri.find("apps")>0:
		uri += str(random.randint(1000,10000))

	resp = numpy.random.choice(response,p=[0.2,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1])
	byt = int(random.gauss(5000,50))
	referer = faker.uri()
	useragent = numpy.random.choice(ualist,p=[0.5,0.3,0.1,0.05,0.05] )()
	f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s "%s" "%s"\n' % (ip,dt,tz,vrb,uri,resp,byt,referer,useragent))

	log_lines = log_lines - 1
	flag = False if log_lines == 0 else True
	if args.sleep:
		time.sleep(args.sleep)
