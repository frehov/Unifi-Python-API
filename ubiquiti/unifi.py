import json
import re
import warnings
from typing import Pattern, Dict, Union

from requests import Session


class LoggedInException(Exception):

    def __init__(self, *args, **kwargs):
        super(LoggedInException, self).__init__(*args, **kwargs)


class API(object):
    """
    Unifi API for the Unifi Controller.

    """
    _login_data = {}
    _current_status_code = None

    def __init__(self,
                 username: str="ubnt",
                 password: str="ubnt",
                 site: str="default",
                 baseurl: str="https://unifi:8443",
                 verify_ssl: bool=True):
        """
        Initiates the api with default settings if none other are set.
        Based off https://ubntwiki.com/products/software/unifi-controller/api

        :param username: username for the controller user
        :param password: password for the controller user
        :param site: which site to connect to (Not the name you've given the
            site, but the url-defined name)
        :param baseurl: where the controller is located
        :param verify_ssl: Check if certificate is valid or not, throws warning
            if set to False
        """
        self._login_data['username'] = username
        self._login_data['password'] = password
        self._site = site
        self._verify_ssl = verify_ssl
        self._baseurl = baseurl
        self._session = Session()
        self._session.verify = self._verify_ssl

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
        url = "{}/api/login".format(self._baseurl)
        with self._session as s:
            r = s.post(url, data=json.dumps(self._login_data))
        if r.status_code == 400:
            raise LoggedInException("Failed to log in to api with provided "
                                    "credentials")

    def logout(self):
        """
        Log the user out

        :return: None
        """
        self._session.get("{}/logout".format(self._baseurl))
        self._session.close()

    def _get(self, url):
        with self._session as s:
            r = s.get(url, data="json={}")
        status_code = r.status_code
        if status_code == 401:
            raise LoggedInException("Invalid login, or login has expired")
        if status_code != 200:
            warnings.warn('Status code of {} received for {}'.format(
                status_code, url
            ))
        return r.json()['data']

    def list_clients(self,
                     filters: Dict[str, Union[str, Pattern]]=None,
                     order_by: str=None) -> list:
        """
        List all available clients from the api

        :param filters: dict with valid key, value pairs, string supplied is
        compiled to a regular expression
        :param order_by: order by a valid client key, defaults to '_id' if key
        is not found
        :return: A list of clients on the format of a dict
        """

        url = "{}/api/s/{}/stat/sta".format(self._baseurl, self._site)
        data = self._get(url)

        if filters:
            for term, value in filters.items():
                value_re = value if isinstance(value, Pattern) else re.compile(value)

                data = [x for x in data if term in x.keys() and
                        re.fullmatch(value_re, x[term])]

        if order_by:
            data = sorted(data, key=lambda x: x[order_by] if order_by in x.keys() else x['_id'])

        return data

    def all_configured_clients(self) -> list:
        """
        List of all configured/known clients on the site. Differs from the above
        as it includes

        :return: list of clients known (dicts)
        """
        url = '{}/api/s/{}/rest/user'.format(self._baseurl, self._site)
        return self._get(url)

    def get_devices(self) -> list:
        """
        List of site devices

        :return: list of devices on site
        """
        url = '{}/api/s/{}/stat/device'.format(self._baseurl, self._site)
        return self._get(url)

    def get_routes(self) -> list:
        """
        All active routes on the device

        :return: list of routes on site
        """
        url = '{}/api/s/{}/stat/routing'.format(self._baseurl, self._site)
        return self._get(url)

    def get_port_forwarding(self) -> list:
        """
        List of routes for site

        :return: list of routes on site
        """
        url = '{}/api/s/{}/rest/portforward'.format(self._baseurl, self._site)
        return self._get(url)


if __name__ == '__main__':
    pass