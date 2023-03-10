import argparse
import logging
import os
from time import sleep
from envoy_solar_reader import __version__

import yaml

from envoy_solar_reader.dataretriever import DataRetriever, LocalDataRetriever
from envoy_solar_reader.envoy_solar_reader import EnvoySolarReader
from envoy_solar_reader.mqtt_service import MqttService
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


def create_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config",
                        help="Full path to config file. If left empty, program will try to load config.yaml from the current directory",
                        default="./config.yaml")
    parser.add_argument("--mode", help="Use api on local device (soon to be deprecated) or use cloud based api ",
                        choices=['local', 'cloud'], default="local")
    parser.add_argument("--loglevel", help="Minimum loglevel, default is INFO",
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default="INFO")
    parser.add_argument("--version", help="Show version", action='store_true')
                        
                        

    return parser

def run():
    argparser = create_argparser()
    args = argparser.parse_args()

    loglevel = getattr(logging, args.loglevel)
    logging.basicConfig(
        level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.version:
        print (__version__)
        exit(0)
        
    if args.mode == 'cloud':
        logger.critical('Cloud api is not implemented yet. Exiting..')
        exit(2)

    logger.info("Loading config from file " + args.config)

    if not os.path.isfile(args.config):
        logger.critical("Config file not found")
        exit(1)

    total_config = yaml.full_load(open(args.config, 'r'))

    local_section = total_config['local']
    reader: DataRetriever = LocalDataRetriever(envoy_host=local_section['envoy_host'],
                                               envoy_user=local_section['envoy_user'],
                                               envoy_password=local_section['envoy_password'],
                                               envoy_serial=local_section['envoy_serial'])
    envoy_solar_reader: EnvoySolarReader = EnvoySolarReader(reader=reader)

    mqtt_section = total_config['mqtt']
    mqtt_client: mqtt.Client = mqtt.Client()
    mqtt_service: MqttService = MqttService(host=mqtt_section['host'], port=mqtt_section['port'], username=mqtt_section['username'], password=mqtt_section['password'], mqtt_client=mqtt_client)
    logger.info(f'Reporting interval = {mqtt_section["report_interval_seconds"]} seconds ')
    mqtt_service.setup()


    TOPIC = 'envoy/production'
    while True:
        try:
            data = envoy_solar_reader.get_production_data()
            mqtt_service.publish_message(TOPIC, data)
            sleep(mqtt_section['report_interval_seconds'])
        except Exception as e:
            logger.error(f"Something went wrong. Retrying after {mqtt_section['report_interval_seconds']}")
            sleep(mqtt_section['report_interval_seconds'])

if __name__ == '__main__':
    run()

