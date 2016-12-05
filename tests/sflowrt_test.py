#!/usr/bin/env python
import requests
import json
import osapi


token_json = osapi.get_user_token("user01", "user01")
print json.dumps(token_json)

# flowurl = 'http://192.168.1.180:8008/flows/json?name=vm0001&maxFlows=20'
# flowID = -1
# while 1 == 1:
#     r = requests.get(flowurl + "&flowID=" + str(flowID))
#     if r.status_code != 200:
#         break
#     flows = r.json()
#     if len(flows) == 0:
#         continue
#     flowID = flows[0]["flowID"]
#     flows.reverse()
#     for f in flows:
#         print json.dumps(f)