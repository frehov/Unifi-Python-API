from Ubiquity.Unifi_API import Unifi
import json

r = Unifi(username="ubnt", password="ubnt", baseurl="https://unifi:8443")

r.login()

device_list = (r.list_sta( filters={"hostname": "Chromecast\-Ultra", "ip" : "192\.168\.0\.\d+"}, order_by="ip"))

print(json.dumps(device_list, indent=4))

r.logout()