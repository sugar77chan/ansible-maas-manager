#!/usr/bin/python3
import sys
import os
import json
import yaml
from requests_oauthlib import OAuth1Session


# 自动查找 all.yaml 的路径（优先 group_vars，再 vars）
def load_config():
    base_dir = os.path.dirname(__file__)
    for rel_path in ['group_vars/all.yaml', 'vars/all.yaml']:
        full_path = os.path.join(base_dir, rel_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
    raise FileNotFoundError("未找到 group_vars/all.yaml 或 vars/all.yaml")


# 加载配置
config = load_config()
MAAS_URL = config['maas_url']
API_KEY = config['api_key']

# 拆分 API KEY
client_key, token_key, token_secret = API_KEY.split(':')
session = OAuth1Session(
    client_key=client_key,
    resource_owner_key=token_key,
    resource_owner_secret=token_secret
)


def get_machines(resource_type):
    url = f"{MAAS_URL}api/2.0/{resource_type}/"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()


def get_os_mapping():
    return {
        "8": "centos8",
        "7": "centos7",
        "bionic": "ubuntu18",
        "focal": "ubuntu20",
        "jammy": "ubuntu22",
        "mantic": "ubuntu23",
        "noble": "ubuntu24"
    }


def build_inventory(machines):
    os_mapping = get_os_mapping()
    inventory = {
        '_meta': {
            'hostvars': {}
        }
    }

    for machine in machines:
        if "Region" or "Rack" in machine['node_type_name']:
            ansible_user = "ubuntu"
            group_name = "controllers"
        elif machine['status_name'] == 'Ready':
            group_name = "ready_machines"
            ansible_user = "ubuntu"
        elif machine['status_name'] == 'Deployed':
            distro = machine.get('distro_series', '').lower()
            if distro not in os_mapping:
                continue
            ansible_user = "ubuntu" if "ubuntu" in os_mapping[distro] else "cloud-user"
            pool = machine.get('pool', {}).get('name', 'default')
            group_name = f"{pool}_{os_mapping[distro]}"
        else:
            continue

        hostname = machine['fqdn']
        ip_list = machine.get('ip_addresses', [])
        ip_address = next((ip for ip in ip_list if ':' not in ip), None)

        if not ip_address:
            continue

        if group_name not in inventory:
            inventory[group_name] = {
                'hosts': []
            }
        if hostname not in inventory[group_name]["hosts"]:
            inventory[group_name]['hosts'].append(hostname)
            inventory['_meta']['hostvars'][hostname] = {
                'ansible_user': ansible_user,
                'system_id': machine.get('system_id'),
                'hostname': machine.get('hostname'),
                'ansible_ssh_host': ip_address
            }

    return inventory


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        all_machines = []
        for resource in ["regioncontrollers", "rackcontrollers", "machines"]:
            all_machines += get_machines(resource)
        inventory = build_inventory(all_machines)
        print(json.dumps(inventory, indent=2))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
