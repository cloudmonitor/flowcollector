# _*_ coding:utf-8 _*_

from multiprocessing import Process, current_process
import pika
from settings import *


class FlowCollect(Process):
    """流量收集类"""
    def __init__(self, url, instance):
        super(FlowCollect, self).__init__()
        self.url = url
        self.instance = instance
        self.name = instance["id"]
        self.flag = True

    def run(self):
        flowID = -1
        headers = {"Accept": "application/json"}
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.180'))
        channel = connection.channel()
        channel.queue_declare(queue='flow', durable=True)
        while 1 == 1 and self.flag:
            r = requests.get(self.url + "&flowID=" + str(flowID), headers=headers, timeout=3)
            if r.status_code != 200:
                break
            flows = r.json()
            if len(flows) == 0:
                time.sleep(1)
                continue
            flowID = flows[0]["flowID"]
            flows_insert = []
            for f in flows:
                flow = {}
                flow["project_id"] = self.instance["tenant_id"]
                flow["instance_id"] = self.instance["id"]
                flow["port_id"] = self.instance["interfaceAttachments"][0]["port_id"]
                flow["mac_addr"] = self.instance["interfaceAttachments"][0]["mac_addr"].replace(":", "").upper()
                flow["fixed_ip"] = self.instance["interfaceAttachments"][0]["fixed_ips"][0]["ip_address"]
                for ips in self.instance["addresses"].values():
                    if len(ips) == 2:
                        for ip in ips:
                            if ip["OS-EXT-IPS:type"] == "floating":
                                flow["floating_ip"] = ip["addr"]
                    else:
                        flow["floating_ip"] = "0.0.0.0"

                flow["hypervisor_name"] = self.instance["OS-EXT-SRV-ATTR:hypervisor_hostname"]
                flow["timestap"] = f["end"]
                flowkeys = f["flowKeys"].split(',')
                flow["macsource"] = flowkeys[0]
                flow["macdestination"] = flowkeys[1]
                flow["ipsource"] = flowkeys[2]
                flow["ipdestination"] = flowkeys[3]
                flow["ipprotocol"] = int(flowkeys[4])
                flow["size"] = float(f["value"])
                flow["srcport_or_icmptype"] = int(flowkeys[5])
                flow["dstport_or_icmpcode"] = int(flowkeys[6])
                flow["tcpflags"] = flowkeys[7]
                flow["httpmethod"] = flowkeys[8]
                flow["extension"] = "{}"
                flows_insert.append(flow)

            channel.basic_publish(exchange='',
                                  routing_key='flow',
                                  body=json.dumps(flows_insert),
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,  # make message persistent
                                      )
                                  )
            print " [%s] Sent %r" % (current_process().pid, json.dumps(flows_insert))
            time.sleep(3)
        connection.close()

