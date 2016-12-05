# _*_ coding:utf-8 _*_

"""sFlow-RT API实现"""

from flowcollector.settings import *
from osapi import get_hypervisor_instances_and_interface
from flowcollector.flowcollect import FlowCollect


def define_flow():
    """针对每一虚拟机定义流"""
    instance_info = get_hypervisor_instances_and_interface()

    for instance in instance_info:
        if instance["OS-EXT-STS:vm_state"] == "active":
            flow_api = FlOW_API % (instance["id"])
            mac_addr = instance["interfaceAttachments"][0]["mac_addr"].replace(":", "").upper()
            flow_define = FLOW_DEFINE % (mac_addr, mac_addr)
            url = SFLOW_RT_API_BASE_URL + flow_api
            r = requests.put(url, flow_define)
            print r.status_code

            # instance["id"]
            # instance["OS-EXT-SRV-ATTR:hypervisor_hostname"]


def get_flow():
    """获取每一个虚拟机产生的流"""
    instance_info = get_hypervisor_instances_and_interface()
    pool = []
    for instance in instance_info:
        if instance["OS-EXT-STS:vm_state"] == "active":
            flow_collcet_api = FLOW_COLLECT_API % (instance["id"])
            url = SFLOW_RT_API_BASE_URL + flow_collcet_api
            # p = Process(target=collect_flow, args=(url, instance))
            p = FlowCollect(url, instance)
            p.daemon = True
            p.start()
            pool.append(p)
            # pool.apply_async(collect_flow, (url, instance))
            # t = threading.Thread(target=collect_flow, args=(url, instance))
            # t.start()
            # pool.append(t)

    for pro in pool:
        pro.join()


def flow_collect():
    pool = []
    while 1 == 1:
        instance_info = get_hypervisor_instances_and_interface()

        for instance in instance_info:
            if instance["OS-EXT-STS:vm_state"] == "active":
                flow_api = FlOW_API % (instance["id"])
                url = SFLOW_RT_API_BASE_URL + flow_api
                ret = requests.get(url)
                if ret.status_code == 404:
                    mac_addr = instance["interfaceAttachments"][0]["mac_addr"].replace(":", "").upper()
                    flow_define = FLOW_DEFINE % (mac_addr, mac_addr)
                    r = requests.put(url, flow_define)
                    if r.status_code == 204:
                        flow_collcet_api = FLOW_COLLECT_API % (instance["id"])
                        collect_url = SFLOW_RT_API_BASE_URL + flow_collcet_api
                        p = FlowCollect(collect_url, instance)
                        p.daemon = True
                        p.start()
                        pool.append(p)

            else:
                flow_api = FlOW_API % (instance["id"])
                url = SFLOW_RT_API_BASE_URL + flow_api
                ret = requests.get(url)
                if ret.status_code == 200:
                    requests.delete(url)
                    for pro in pool:
                        if pro.name == instance["id"]:
                            pro.flag = False
                            pool.remove(pro)

        time.sleep(60)

if __name__ == "__main__":
    flow_collect()
