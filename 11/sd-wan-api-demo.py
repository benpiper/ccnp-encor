import json, requests, urllib3
from requests.auth import HTTPBasicAuth
s = requests.Session()
data =  { 'j_username':  'devnetuser', 'j_password':  'RG!_Yw919_83' }
url = "https://sandbox-sdwan-2.cisco.com/j_security_check"
response = s.post(url, data=data, verify=False)
print(response.status_code)

url = "https://sandbox-sdwan-2.cisco.com/dataservice/device/omp/routes/received?deviceId=10.0.0.3"
response = s.get(url, verify=False)
keys = ("prefix", "from-peer", "originator", "status")
result = [{k: item.get(k) for k in keys} for item in response.json()["data"]]
print(json.dumps(result, indent=2))
