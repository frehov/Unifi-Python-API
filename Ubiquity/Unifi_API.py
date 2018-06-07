from requests import Session
import json
import re


class Unifi(object):
    _login_data = {}

    def __init__(self, username: str="ubnt", password: str="ubnt", site: str="default", baseurl: str="https://unifi:8443", verify_ssl=True):
        self._login_data['username'] = username
        self._login_data['password'] = password
        self._site = site
        self._verify_ssl = verify_ssl
        self._baseurl = baseurl
        self._session = Session()

    def login(self):
        print(json.dumps(self._login_data))
        self._session.post("{}/api/login".format(self._baseurl), data=json.dumps(self._login_data), verify=False)

    def logout(self):
        self._session.get("{}/logout".format(self._baseurl))
        self._session.close()

    def list_sta(self, filters: dict=None, order_by: str=None) -> list:
        r = self._session.get( "{}/api/s/{}/stat/sta".format(self._baseurl, self._site), data="json={}").json()
        data = r['data']
        if filters:
            for term, value in filters.items():
                print(term)
                value_re = re.compile(value)
                data = [x for x in data if term in x.keys() and re.fullmatch(value_re, x[term])]
        if order_by:
            data = sorted(data, key=lambda x: x[order_by] if order_by in x.keys() else x['_id'])

        return data
