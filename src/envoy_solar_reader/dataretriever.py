import json
import logging
from abc import ABC, abstractmethod

import requests
from requests import Response

from envoy_solar_reader.models import ProductionData

logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


class DataRetriever(ABC):
    @abstractmethod
    def get_production_data(self) -> ProductionData:
        pass


class LocalDataRetriever(DataRetriever):

    def __init__(self, envoy_host: str, envoy_user: str, envoy_password: str, envoy_serial: str):
        self._envoy_host: str = envoy_host
        self._envoy_user: str = envoy_user
        self._envoy_password: str = envoy_password
        self._envoy_serial: str = envoy_serial

        self._login_url: str = 'https://enlighten.enphaseenergy.com/login/login.json?'
        self._token_url: str = 'https://entrez.enphaseenergy.com/tokens'

        self._token: str = ''
        self._session: requests.Session = requests.Session()

    def _get_response_data(self, response: Response) -> str:
        if response.status_code != 200:
            raise RequestError(response.status_code, response.text)

        return response.text

    def _do_get_request(self, url: str, data=None, json=None, headers={}) -> str:
        response: Response = Response()
        if data:
            response = requests.get(url, data=data, headers=headers, verify=False)
        elif json:
            response = requests.get(url, json=json, headers=headers, verify=False)


    def _get_token(self):
        logger.info('Getting token...')
        login_data = {'user[email]': self._envoy_user, 'user[password]': self._envoy_password}

        logger.debug(f'Logging in to {self._login_url}')
        login_response = self._session.post(self._login_url, data=login_data, verify=False)
        login_data = json.loads(self._get_response_data(login_response))

        logger.debug(f'Get token from {self._token_url}')
        token_request_data = {'session_id': login_data['session_id'], 'serial_num': self._envoy_serial,
                              'username': self._envoy_user}
        token_response = self._session.post(self._token_url, json=token_request_data, verify=False)
        self._token = self._get_response_data(token_response)
        logger.info('Token successfully retrieved..')

    def get_production_data(self) -> ProductionData:
        url = f'https://{self._envoy_host}/api/v1/production'
        logger.info(f"Getting PV production data from {url}..")

        if self._token == '':
            logger.info('No token set')
            self._get_token()

        headers = {'Authorization': 'Bearer ' + self._token}
        try:
            response = self._session.get(url, headers=headers, verify=False)
            data = self._get_response_data(response)
            logger.debug(f"Raw data returned: {data}")

            data_dict = json.loads(data)
            return ProductionData(currentTotalPowerInWatts=data_dict['wattsNow'],
                                  energyProducedTodayInKwh=data_dict['wattHoursToday'] / 1000)
        except RequestError as e:
            if e.status_code == 401:
                logger.info('Invalid token or token expired. Get new one..')
                self._get_token()
                return self.get_production_data()


class RequestError(Exception):
    def __init__(self, status_code: int, response_msg: str):
        self.status_code = status_code
        self.response_msg = response_msg
