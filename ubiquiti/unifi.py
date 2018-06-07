from requests import Session
import json
import re
from typing import Pattern, Dict, Union


class LoggedInException(Exception):

    def __init__(self, *args, **kwargs):
        super(LoggedInException, self).__init__(*args, **kwargs)


class API(object):
    """
    Unifi API for the Unifi Controller.

    """
    _login_data = {}
    _current_status_code = None

    def __init__(self, username: str="ubnt", password: str="ubnt", site: str="default", baseurl: str="https://unifi:8443", verify_ssl: bool=True):
        """
        Initiates tha api with default settings if none other are set.

        :param username: username for the controller user
        :param password: password for the controller user
        :param site: which site to connect to (Not the name you've given the site, but the url-defined name)
        :param baseurl: where the controller is located
        :param verify_ssl: Check if certificate is valid or not, throws warning if set to False
        """
        self._login_data['username'] = username
        self._login_data['password'] = password
        self._site = site
        self._verify_ssl = verify_ssl
        self._baseurl = baseurl
        self._session = Session()

    def __enter__(self):
        """
        Contextmanager entry handle

        :return: isntance object of class
        """
        self.login()
        return self

    def __exit__(self, *args):
        """
        Contextmanager exit handle

        :return: None
        """
        self.logout()

    def login(self):
        """
        Log the user in

        :return: None
        """
        self._current_status_code = self._session.post("{}/api/login".format(self._baseurl), data=json.dumps(self._login_data), verify=self._verify_ssl).status_code
        if self._current_status_code == 400:
            raise LoggedInException("Failed to log in to api with provided credentials")

    def logout(self):
        """
        Log the user out

        :return: None
        """
        self._session.get("{}/logout".format(self._baseurl))
        self._session.close()

    def list_clients(self, filters: Dict[str, Union[str, Pattern]]=None, order_by: str=None) -> list:
        """
        List all available clients from the api

        :param filters: dict with valid key, value pairs, string supplied is compiled to a regular expression
        :param order_by: order by a valid client key, defaults to '_id' if key is not found
        :return: A list of clients on the format of a dict
        """

        r = self._session.get("{}/api/s/{}/stat/sta".format(self._baseurl, self._site, verify=self._verify_ssl), data="json={}")
        self._current_status_code = r.status_code
        
        if self._current_status_code == 401:
            raise LoggedInException("Invalid login, or login has expired")

        data = r.json()['data']

        if filters:
            for term, value in filters.items():
                value_re = value if isinstance(value, Pattern) else re.compile(value)

                data = [x for x in data if term in x.keys() and re.fullmatch(value_re, x[term])]

        if order_by:
            data = sorted(data, key=lambda x: x[order_by] if order_by in x.keys() else x['_id'])

        return data
