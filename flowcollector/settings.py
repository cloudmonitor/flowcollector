# _*_ coding:utf-8 _*_

""" sFlow-RT的基本信息以及一些必要的库"""

import requests
import json
import time
import datetime

FLOWDB_CONN = "mongodb://flowdb:flowdb@192.168.1.180:27017/flowdb"

SFLOW_RT_API_BASE_URL = 'http://192.168.1.180:8008'

# 对流增删改查
FlOW_API = '/flow/%s/json'

# 获取流?name=flowname
FLOW_COLLECT_API = '/flows/json?name=%s&maxFlows=20'

FLOW_DEFINE = '''{
  "filter": "macsource=%s|macdestination=%s",
  "t": 2,
  "log": true,
  "keys": "macsource,macdestination,ipsource,ipdestination,ipprotocol,or:tcpsourceport:udpsourceport:icmptype:-1,or:tcpdestinationport:udpdestinationport:icmpcode:-1,null:tcpflags:000000000,null:httpmethod:unknown,null:direction:unknown",
  "activeTimeout": 10,
  "value": "bytes",
  "fs": ",",
  "n": 5
}'''

