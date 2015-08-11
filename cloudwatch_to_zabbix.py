#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cloudwatch_to_zabbix: A cmd tools to send aws cloudwatch data to zabbix server
    example:  get aws elb latency : ./cloudwatch_to_zabbix.py --region us-east-1 --metric_name 'Latency' --dimension_name 'LoadBalancerName' --dimension_value 'API'  --namespace "AWS/ELB" --statistics "Average"
    author: songjiao
    date: 2015/8/10
"""
import json
import sys
import logging
from optparse import OptionParser
import datetime
import socket
import struct

import boto.ec2.cloudwatch


class ZabbixSender:

        def __init__(self, server_host, server_port = 10051):
                self.server_ip = socket.gethostbyname(server_host)
                self.server_port = server_port

        def send(self, host, key, value):
            DATA = r'''{
                    "request":"sender data",
                    "data":[
                        {
                        "host":"%s",
                        "key":"%s",
                        "value":"%s"
                        }
                    ]
                }
                ''' % (host, key, value)
            HEADER = '''ZBXD\1%s%s'''
            data_length = len(DATA)
            data_header = struct.pack('i', data_length) + '\0\0\0\0'

            data_to_send = HEADER % (data_header, DATA)

            # here really should come some exception handling
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_ip, self.server_port))


            # send the data to the server
            sock.send(data_to_send)

            # read its response, the first five bytes are the header again
            response_header = sock.recv(5)
            if not response_header == 'ZBXD\1':
                raise ValueError('Got invalid response')

            # read the data header to get the length of the response
            response_data_header = sock.recv(8)
            response_data_header = response_data_header[:4] # we are only interested in the first four bytes
            response_len = struct.unpack('i', response_data_header)[0]

            # read the whole rest of the response now that we know the length
            response_raw = sock.recv(response_len)

            sock.close()

            response = json.loads(response_raw)

            return response



if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    #Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)


    optp.add_option("-r", "--region", dest="region",
                    help="set aws region")

    optp.add_option("-p", "--period", dest="period",type="int",default=300,
                    help="The granularity, in seconds, of the returned datapoints. Period must be at least 60 seconds and must be a multiple of 60")

    # optp.add_option("-s", "--start_time", dest="start_time",
    #                 help="The time stamp to use for determining the first datapoint to return.")
    #
    # optp.add_option("-e", "--end_time", dest="end_time",
    #                 help="The time stamp to use for determining the last datapoint to return.")

    optp.add_option("-m", "--metric_name", dest="metric_name",
                    help="The metric name.")


    optp.add_option("-n", "--namespace", dest="namespace",
                    help="The metric s namespace.")


    optp.add_option("-s", "--statistics", dest="statistics",
                    help="A list of statistics names Valid values: Average  Sum  SampleCount  Maximum Minimum")


    optp.add_option("-N", "--dimension_name", dest="dimension_name",
                    help="dimession name")

    optp.add_option("-V", "--dimension_value", dest="dimension_value",
                    help="dimession value")

    optp.add_option("-u", "--unit", dest="unit",
                    help="The unit for the metrics,check: http://boto.readthedocs.org/en/latest/ref/cloudwatch.html#module-boto.ec2.cloudwatch.metric for more detail")


    optp.add_option("-z","--zabbix_server",dest="zabbix_server",
                    help="zabbix server" ,default="127.0.0.1")

    optp.add_option("-P","--zabbix_port",dest="zabbix_port",type="int",
                    help="zabbix port", default=10051)

    optp.add_option("-k","--zabbix_key",dest="zabbix_key",
                    help="zabbix port")

    optp.add_option("-H","--zabbix_host",dest="zabbix_host",
                    help="zabbix host")

    optp.add_option("-R","--raw_run",dest="raw_run",
                    help="only get data from cloudwatch,don't submit to zabbix")


    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')
    logger = logging.getLogger()


    if opts.region is None:
        logging.error("region not set,run with -r or --region" )
        sys.exit(-1)





    if opts.zabbix_key is None:
        logger.error("zabbix_key not set,run with --zabbix_key")
        sys.exit(-1)

    if opts.zabbix_host is None:
        logger.error("zabbix_host not set,run with --zabbix_host")
        sys.exit(-1)


    if opts.metric_name is None:
        logger.error("metric_name not set,run with --metric_name")
        sys.exit(-1)

    if opts.dimension_name is None:
        logger.error("dimension_name not set ,run with --dimension_name")
        sys.exit(-1)

    if opts.dimension_value is None:
        logger.error("dimension_value not set ,run with --dimension_value")
        sys.exit(-1)


    if opts.namespace is None:
        logger.error("namespace not set, run with --namespace")
        sys.exit(-1)

    if opts.statistics is None:
        logger.error("statistics not set,run with --statistics")
        sys.exit(-1)

    if opts.raw_run is None:
        opts.raw_run = False
    else:
        opts.raw_run= True


    conn = boto.ec2.cloudwatch.connect_to_region(opts.region)
    rs=conn.get_metric_statistics(opts.period,datetime.datetime.utcnow() - datetime.timedelta(seconds=opts.period),datetime.datetime.utcnow(),opts.metric_name,opts.namespace,opts.statistics,dimensions={opts.dimension_name:opts.dimension_value})

    logger.debug(r"cloudwatch raw data: %s" %(rs))

    if not opts.raw_run:
        sender = ZabbixSender(opts.zabbix_server,opts.zabbix_port)
        value = 0
        if len(rs)>0:
            data=rs[0]
            value = data[opts.statistics]
        else:
            logger.info("No data Found")
        logger.info("send data to zabbix, key=%s   value=%s" %(opts.zabbix_key,value))
        respond = sender.send(opts.zabbix_host,opts.zabbix_key,value)
        logger.info(respond)

