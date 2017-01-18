# _*_ coding:utf-8 _*_


import requests
from gethostname import gethostname


CREDENTIAL_PASSWORD = '{"auth": {"tenantName": "%s", "passwordCredentials": {"username": "%s", "password": "%s"}}}'
KEYSTONE_ENDPOINT = 'http://controller:5000/v2.0'
NOVA_ENDPOINT = 'http://controller:8774/v2/{tenant_id}'


def get_admin_token():
    """"获取admin的token"""
    credential = CREDENTIAL_PASSWORD % ('admin', 'admin', 'admin')
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.post(KEYSTONE_ENDPOINT+'/tokens', data=credential, headers=headers)
    return r.json()


def get_all_tenant_instances():
    """获取所有租户下所有的VM（超级管理员权限）"""
    admin_token = get_admin_token()
    admin_token_id = admin_token['access']['token']['id']
    admin_tenant_id = admin_token['access']['token']['tenant']['id']
    headers = {"Content-type": "application/json", "X-Auth-Token": admin_token_id, "Accept": "application/json"}
    url = NOVA_ENDPOINT.format(tenant_id=admin_tenant_id)
    r = requests.get(url+'/servers/detail?all_tenants=1', headers=headers)
    return r.json()


def get_hypervisor_instances_and_interface():
    """获取计算节点上所有的VM以及相应接口信息（超级管理员权限）"""
    admin_token = get_admin_token()
    admin_token_id = admin_token['access']['token']['id']
    admin_tenant_id = admin_token['access']['token']['tenant']['id']
    hypervisor_servers_list = []
    headers = {"Content-type": "application/json", "X-Auth-Token": admin_token_id, "Accept": "application/json"}
    url = NOVA_ENDPOINT.format(tenant_id=admin_tenant_id)
    all_instance_info = get_all_tenant_instances()
    all_tenants = get_all_tenants(admin_token_id)
    hostname = gethostname()
    for instance in all_instance_info['servers']:
        if instance['OS-EXT-SRV-ATTR:hypervisor_hostname'] == hostname:
            r = requests.get(url + '/servers/' + instance['id'] + "/os-interface", headers=headers)
            instance['interfaceAttachments'] = r.json()['interfaceAttachments']
            tenant_name = _get_instance_tenant_name(instance["tenant_id"], all_tenants)
            instance["tenant_name"] = tenant_name
            hypervisor_servers_list.append(instance)
    return hypervisor_servers_list


def get_all_tenants(token_id):
    """获得所有的租户信息，并进行过滤掉service项目"""
    headers = {"Content-type": "application/json", "X-Auth-Token": token_id, "Accept": "application/json"}
    url = "http://controller:35357/v2.0/tenants"
    r = requests.get(url=url, headers=headers)
    tenants = r.json()
    del_tenants = []
    for tenant in tenants["tenants"]:
        if tenant["name"] == "service":
            del_tenants.append(tenant)
    for del_tenant in del_tenants:
        tenants["tenants"].remove(del_tenant)
    return tenants


def _get_instance_tenant_name(instance_tenant_id, tenants):
    tenant_name = "unknown"
    for tenant in tenants["tenants"]:
        if instance_tenant_id == tenant["id"]:
            tenant_name = tenant["name"]
            break
    return tenant_name


if __name__ == "__main__":
    import json
    print json.dumps(get_hypervisor_instances_and_interface())
