# _*_ coding:utf-8 _*_

"""sFlow-RT API实现"""

import os
import signal
from settings import *
from getinstance import get_hypervisor_instances_and_interface
from flowcollect import FlowCollect


def flow_collect():
    pool = []
    while 1 == 1:
        # 获取虚拟机信息
        instance_info = get_hypervisor_instances_and_interface()
        # 删除 由于虚拟机删除所遗留的采集进程以及采集流量项
        for pro in pool:
            is_delete = True
            for instance in instance_info:
                if pro.name == instance["id"]:
                    is_delete = False
                    break
            if is_delete:
                flow_api = FlOW_API % (pro.name, )
                url = SFLOW_RT_API_BASE_URL + flow_api
                ret = requests.get(url)
                if ret.status_code == 200:
                    requests.delete(url)
                pro.flag = False
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
        # 每隔一分钟检测一次
        time.sleep(60)

if __name__ == "__main__":
    flow_collect()
