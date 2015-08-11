��cloudwatch�����ݵ���zabbix�Ĺ���
===================================


        Usage: cloudwatch_to_zabbix.py [options]

        Options:
          -h, --help            show this help message and exit
          -q, --quiet           set logging to ERROR
          -d, --debug           set logging to DEBUG
          -v, --verbose         set logging to COMM
          -r REGION, --region=REGION
                                set aws region
          -p PERIOD, --period=PERIOD
                                The granularity, in seconds, of the returned
                                datapoints. Period must be at least 60 seconds and
                                must be a multiple of 60
          -m METRIC_NAME, --metric_name=METRIC_NAME
                                The metric name.
          -n NAMESPACE, --namespace=NAMESPACE
                                The metric s namespace.
          -s STATISTICS, --statistics=STATISTICS
                                A list of statistics names Valid values: Average  Sum
                                SampleCount  Maximum Minimum
          -N DIMENSION_NAME, --dimension_name=DIMENSION_NAME
                                dimession name
          -V DIMENSION_VALUE, --dimension_value=DIMENSION_VALUE
                                dimession value
          -u UNIT, --unit=UNIT  The unit for the metrics,check: http://boto.readthedoc
                                s.org/en/latest/ref/cloudwatch.html#module-
                                boto.ec2.cloudwatch.metric for more detail
          -z ZABBIX_SERVER, --zabbix_server=ZABBIX_SERVER
                                zabbix server
          -P ZABBIX_PORT, --zabbix_port=ZABBIX_PORT
                                zabbix port
          -k ZABBIX_KEY, --zabbix_key=ZABBIX_KEY
                                zabbix port
          -H ZABBIX_HOST, --zabbix_host=ZABBIX_HOST
                                zabbix host
          -R RAW_RUN, --raw_run=RAW_RUN
                                only get data from cloudwatch,don't submit to zabbix


ԭ��
==========
����boto api��cloudwatch��ȡaws�ļ�����ݣ�Ȼ������zabbix_senderЭ�齫�����ύ��zabbix ����������ľ���item


ʾ��
===========
����������ѷ���¼��½ڵ���һ������api��ELB������ϣ��������ELB���ӳ�(Latency)�ʹ����ʣ�Zabbix ��������IPΪ1.1.1.1�����Ƕ���������ݵ�hostΪAWS-ELB-SGP��Host �ﶨ����ITEM��aws.elb.latency���ڼ�¼�ӳ�����,Item:aws.elb.ELB5XX���ڼ�¼������



        ./cloudwatch_to_zabbix.py --period=60 --region ap-southeast-1 --metric_name 'Latency' --dimension_name 'LoadBalancerName' --dimension_value 'api'  --namespace "AWS/ELB" --statistics "Average" --zabbix_key aws.elb.latency --zabbix_host 'AWS-ELB-SGP' --zabbix_server 1.1.1.1
        ./cloudwatch_to_zabbix.py --period=60 --region ap-southeast-1 --metric_name 'HTTPCode_ELB_5XX' --dimension_name 'LoadBalancerName' --dimension_value 'api'  --namespace "AWS/ELB" --statistics "Sum" --zabbix_key aws.elb.latency --zabbix_host 'AWS-ELB-SGP' --zabbix_server 1.1.1.1


�ο�����
========
- [boto cloudwatch api] (http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/elb-metricscollected.html)
- [aws cloudwatch metric] (http://boto.readthedocs.org/en/latest/ref/cloudwatch.html#module-boto.ec2.cloudwatch.metric)

