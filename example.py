from ubiquiti.unifi import API as Unifi_API
import json


# Example with context manager
with Unifi_API(username="admin ", password="ubnt", baseurl="https://unifi:8443", verify_ssl=True) as api:
    device_list = (api.list_clients(filters={'hostname': 'Chromecast.*'}, order_by="ip"))
    print(json.dumps(device_list, indent=4))


# Example without contextmanager
api = Unifi_API(username="ubnt", password="ubnt", baseurl="https://unifi:8443", verify_ssl=True)
api.login()
device_list = (api.list_clients(order_by="ip"))
print(json.dumps(device_list, indent=4))
api.logout()