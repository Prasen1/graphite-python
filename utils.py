import yaml

import log

import dateutil.parser as dp

import socket



conf_graphite = yaml.safe_load(open('./config/config_graphite.yaml'))

conf = yaml.safe_load(open('./config/config_catchpoint.yaml'))

logger = log.get_logger(__name__,conf['log_file'],conf['log_level'])



class Utils():

    sock = socket.socket()

    @staticmethod

    def connect_socket():

        server = conf_graphite['carbon_server']

        port = conf_graphite['carbon_port']

        try:

            Utils.sock.connect( (server, port) )

        except socket.error:

            logger.error("Couldn't connect to {} on port {}".format(server,port))

    

    @staticmethod

    def parse_raw(structure):

        synthetic_metrics = []

        if 'error' in structure:

            logger.error(structure['error'])

        if 'detail' not in structure:

            logger.error(structure)

            return None

        logger.info('Parsing data for Graphite')

        logger.info('Data StartTimestamp: {} EndTimestamp: {}'.format(structure['start'],structure['end']))

  

        test_params = []

        final_list = [] #list of all objects

        synthetic_metrics = structure['detail']['fields']['synthetic_metrics']



        for i in synthetic_metrics:

            metrics = i['name'].replace(" ", "") #remove whitespace from metric names

            test_params.append(metrics)

        

        for value in structure['detail']['items']:

            values = {} # dictionary which contains tags metrics time 

            tag = {

                'test_id' : value['breakdown_1']['id'],

                'node_id' : value['breakdown_2']['id']

            }

            values['tags'] = tag

            values['time_stamp'] = dp.parse(value['dimension']['name']).timestamp() # convert the timestamp from api response to epoch

            metric_values = value['synthetic_metrics']

            fields = {}

            for i in range(0,len(metric_values),1):

                fields[test_params[i]]=metric_values[i]

            values['metrics'] = fields

            final_list.append(values)

        return final_list



    @staticmethod

    def insert_to_carbon(data): 

        """ 

        Convert dict objects to lines of metrics in the format- my.series;tag1=value1;tag2=value2 metric_value timestamp

        Then send the lines of metrics to carbon listener for storage. Metric path: system.cp.testdata.MetricName

        No added delay between messages as carbon cache handles it

        """



        lines = []        

        try:

            for item in data:

                for key in item['metrics']:

                    lines.append("system.cp.testdata.{};testId={};nodeId={} {} {}".format(key, item['tags']['test_id'], item['tags']['node_id'], item['metrics'][key], item['time_stamp']))

            message = '\n'.join(lines) + '\n' #all lines must end in a newline

            logger.info('Inserting data\n Number of series to update {}'.format(len(message)))

            Utils.sock.sendall(message.encode('utf-8')) # sends lines of data as socket message to carbon listener over TCP

            logger.info('Finished inserting data')        

        except Exception as e:

            logger.exception(str(e))

            logger.exception('Error while inserting data')



    @staticmethod

    def close_socket():

        Utils.sock.close() 



    @staticmethod

    def validate_configurations():

        if 'client_id' not in conf or conf['client_id'] is None:

            return False

        if 'client_secret' not in conf or conf['client_secret'] is None:

            return False

        if 'protocol' not in conf or conf['protocol'] is None: 

            return False

        if 'domain' not in conf or conf['domain'] is None:

            return False 

        if 'token_endpoint' not in conf or conf['token_endpoint'] is None: 

            return False

        if 'rawdata_endpoint' not in conf or conf['rawdata_endpoint'] is None:

            return False

        return True

