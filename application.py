import logger
import yaml
import request_handler
import utils,log

catchpoint_config = './config/config_catchpoint.yaml'
conf = yaml.safe_load(open(catchpoint_config))
logger = log.get_logger(__name__,conf['log_file'],conf['log_level'])

# Makes test ids into batches and fetches data and stores for each batch
class Application(object):
    
    def __init__(self):
        self.__request_handler = request_handler.Catchpoint()

    # Function to create batch of test_ids
    def batch(self,iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    # main function to fetch and store data and throw an exception if authorization fails or if response has no data
    def run(self):    
        try:
            self.__request_handler.authorize(conf)
            utils.Utils.connect_socket() # create the socket connection to server:port specified in config

            for test_id_type in conf['test_ids'].values():
                final_list = []
                for test_id in self.batch(test_id_type, conf['batch_size']):
                    conf['test_id_params']=",".join(test_id)
                    data = self.__request_handler.fetch_data(conf)
                    expired = self.__request_handler.expired_token_check(data)
                    if expired is True:
                        self.__request_handler.authorize(conf)
                        data = self.__request_handler.fetch_data(conf)  
                    parsed_json = utils.Utils.parse_raw(data)
                    if final_list is []:
                        final_list=parsed_json
                    else:
                        if parsed_json:
                            final_list.extend(parsed_json)                
                if final_list:
                    utils.Utils.insert_to_carbon(final_list)
                else:
                    logger.info('No Test ID or Data. Ignoring batch')                
        except Exception as e:
            logger.exception(str(e))
        finally:
            utils.Utils.close_socket() # close the socket connection

# Run main function
if __name__ == '__main__':
    if not utils.Utils.validate_configurations():
        raise RuntimeError('Missing configrations')
    Application().run()
