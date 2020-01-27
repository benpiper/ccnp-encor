import json
import requests
import urllib3
from requests.auth import HTTPBasicAuth
# Authenticate to the vManage controller. It uses cookies for authentication, so we won't have to manually store and pass a token as before.
s = requests.Session()
data =  {
            'j_username':  "devnetuser",
            'j_password':  "Cisco123!"
        }
url = "https://sandboxsdwan.cisco.com:8443/j_security_check"
response = s.post(url, data=data, verify=False)
# Use the vManage API to view the OMP routes being advertised to the vEdge Cloud (cEdge) router with the IP address 4.4.4.60.
url = "https://sandboxsdwan.cisco.com:8443/dataservice/device/omp/routes/received?deviceId=4.4.4.60"
response = s.get(url, data=data, verify=False)
# The response contains column heading definitions, so to show only the interesting information, we'll restrict the output to the "data" object.
print(json.dumps(response.json()["data"], indent=2))