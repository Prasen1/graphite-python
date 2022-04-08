import yaml
import log
import dateutil.parser as dp
import socket

graphite_config = './config/config_graphite.yaml'
catchpoint_config = './config/config_catchpoint.yaml'
conf_graphite = yaml.safe_load(open(graphite_config))
conf = yaml.safe_load(open(catchpoint_config))
logger = log.get_logger(__name__,conf['log_file'],conf['log_level'])

class Utils():

    sock = socket.socket()
    # Create a socket connection
    @staticmethod
    def connect_socket():
        server = conf_graphite['carbon_server']
        port = conf_graphite['carbon_port']
        try:
            Utils.sock.connect( (server, port) )
        except socket.error:
            logger.error("Couldn't connect to {0} on port {1}".format(server,port))
   
    # Parse raw data from catchpoint
    @staticmethod
    def parse_raw(structure):
        synthetic_metrics = []
        if 'error' in structure:
            logger.error(structure['error'])
        if 'detail' not in structure:
            logger.error('No data available',structure)
            return None
        logger.info('Parsing data for Graphite')
        logger.info('Data StartTimestamp: {0} EndTimestamp: {1}'.format(structure['start'],structure['end']))  
        test_params = []
        final_list = [] 
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
            if 'step' in value:
                tag['step'] = value['step']
            if 'hop_number' in value:
                tag['hop_number'] = value['hop_number']
            values['tags'] = tag
            values['time_stamp'] = dp.parse(value['dimension']['name']).timestamp() # convert the timestamp from API response to epoch
            metric_values = value['synthetic_metrics']
            fields = {}
            for i in range(0,len(metric_values),1):
                fields[test_params[i]]=metric_values[i]
            values['metrics'] = fields
            final_list.append(values)
        return final_list
 
    # Convert dict objects to lines of metrics in the format- my.series;tag1=value1;tag2=value2 metric_value timestamp
    # Then send the lines of metrics to carbon listener for storage. Metric path: system.cp.testdata.MetricName
    @staticmethod
    def insert_to_carbon(data): 
        lines = []        
        try:
            for item in data:
                for key in item['metrics']:
                    if 'step' in item['tags']:
                        lines.append("system.cp.testdata.{0};testId={1};nodeId={2};stepNumber={3} {4} {5}".format(key, item['tags']['test_id'], item['tags']['node_id'], item['tags']['step'], item['metrics'][key], int(item['time_stamp'])))
                    elif 'hop_number' in item['tags']:
                        lines.append("system.cp.testdata.{0};testId={1};nodeId={2};hopNumber={3} {4} {5}".format(key, item['tags']['test_id'], item['tags']['node_id'], item['tags']['hop_number'], item['metrics'][key], int(item['time_stamp'])))
                    else:
                        lines.append("system.cp.testdata.{0};testId={1};nodeId={2} {3} {4}".format(key, item['tags']['test_id'], item['tags']['node_id'], item['metrics'][key], int(item['time_stamp'])))
            message = '\n'.join(lines) + '\n' #all lines must end in a newline            
            logger.info('Inserting data\n Number of series to update {}'.format(len(message)))
            Utils.sock.sendall(message.encode('utf-8')) # sends lines of data as socket message to carbon listener over TCP
            logger.info('Finished sending data')        
        except Exception as e:
            logger.exception(str(e))
            logger.exception('Error while inserting data')

    # Close the socket connection
    @staticmethod
    def close_socket():
        Utils.sock.close() 

    # Check for missing configuration
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
