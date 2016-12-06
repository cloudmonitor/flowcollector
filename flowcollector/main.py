# _*_ coding:utf-8 _*_

"""sFlow-RT API实现"""

import os
import signal
from settings import *
from getinstance import get_hypervisor_instances_and_interface
from flowcollect import FlowCollect


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

        # 删除 由于虚拟机删除所遗留的采集进程以及采集流量项
        for pro in pool:
            kill = True
            for instance in instance_info:
                if pro.name == instance["id"]:
                    kill = False
                    break
            if kill:
                flow_api = FlOW_API % (pro.name)
                url = SFLOW_RT_API_BASE_URL + flow_api
                ret = requests.get(url)
                if ret.status_code == 200:
                    requests.delete(url)
                pro.flag = False
                # os.kill(pro.pid, signal.SIGTERM)
                pro.terminate()
                pool.remove(pro)

        # 针对每个虚拟机创建流量采集进程
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
                elif ret.status_code == 200:
                    pro_exist = False
                    for pro in pool:
                        if pro.name == instance["id"]:
                            pro_exist = True
                            break
                    if not pro_exist:
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
                            pro.terminate()
                            pool.remove(pro)


        time.sleep(60)

if __name__ == "__main__":
    flow_collect()
