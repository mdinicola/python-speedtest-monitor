import configparser
import requests

config = configparser.ConfigParser()
config.read('config/config.ini')


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


def send_pushover_message(message: str, config: dict):
    url = 'https://api.pushover.net/1/messages.json'
    payload = {
        "message": message,
        "user": config.get('pushover', 'user_id'),
        "token": config.get('pushover', 'api_token'),
        "sound": config.get('pushover', 'sound')
    }
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception('Could not send pushover message')


download_speed = get_download_speed(config)
message = f'Current Download:\n{download_speed}'

print(message)
