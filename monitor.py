import asyncio
import configparser
import requests
import time
import logging
import os
from datetime import datetime
from pathlib import Path
from asuswrtspeedtest import SpeedtestClient


def get_download_speed(config: dict):
    scheme = 'http'
    if config.getboolean('speedtest_tracker', 'use_https') == True:
        scheme = 'https'

    host = config.get('speedtest_tracker', 'host')
    port = config.get('speedtest_tracker', 'port')
    url = f'{scheme}://{host}:{port}/api/speedtest/latest'

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Could not get latest speedtest result")

    data = (response.json())['data']
    return data['download']


def convert_bps_to_mbps(bps: int):
    mbps = (bps * 8) / (1000 * 1000)
    return mbps


def is_speedtest_current(current_timestamp: int, speedtest_time: str):
    parsed_speedtest_time = datetime.strptime(speedtest_time, '%Y-%m-%dT%H:%M:%S%z')
    speedtest_timestamp = int(datetime.timestamp(parsed_speedtest_time))

    if current_timestamp > speedtest_timestamp:
        return True

    return False


def send_pushover_message(message: str, config: dict):
    if config.getboolean('pushover', 'enabled'):
        url = 'https://api.pushover.net/1/messages.json'
        payload = {
            "message": message,
            "user": config.get('pushover', 'user_id'),
            "token": config.get('pushover', 'api_token'),
            "sound": config.get('pushover', 'sound'),
            "priority": config.getint('pushover', 'priority')
        }
        response = requests.post(url, data=payload)

        if response.status_code != 200:
            raise Exception('Could not send pushover message')


async def main():
    download_speed = float(get_download_speed(config))

    if download_speed < config.getint('monitor', 'download_threshold'):
        message = f'Download Speed: {download_speed}'
        if config.getboolean('asus_router', 'run_speedtest'):
            current_timestamp = int(time.time())
            async with SpeedtestClient(config) as speedtest_client:
                await speedtest_client.run()
                latest_speedtest_result = (await speedtest_client.asus_get_speedtest_history())[0]

            if not is_speedtest_current(current_timestamp, latest_speedtest_result['timestamp']):
                message += '\nRouter speedtest did not run'
                send_pushover_message(message, config)
                logger.info(message)
                return

            router_speed_mbps = convert_bps_to_mbps(latest_speedtest_result['download']['bandwidth'])
            router_speed = '{:0.2f}'.format(router_speed_mbps)
            message += f'\nRouter Download Speed: {router_speed}'

        send_pushover_message(message, config)
        logger.info(message.replace('\n', ' - '))


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    level=logging.INFO
)

current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = f'{current_dir}/logs'

Path(log_dir).mkdir(exist_ok=True)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')

file_handler = logging.FileHandler(f'{log_dir}/monitor.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger = logging.getLogger('SpeedTestMonitor')
logger.addHandler(file_handler)

config = configparser.ConfigParser()
config.read(f'{current_dir}/config/config.ini')

try:
    asyncio.run(main())
except Exception as e:
    message = 'Error occurred. Check log for details'
    send_pushover_message(message, config)
    logger.error(f'{e}')
