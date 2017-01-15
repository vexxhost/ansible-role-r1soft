#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport


def _get_agent(transport, hostname):
    client = Client('http://localhost:9080/Agent?wsdl', transport=transport)
    agents = client.service.getAgents()

    for agent in agents:
        if hostname == agent.hostname:
            return agent
    return None


def _get_disk_safe(client, description):
    safes = client.service.getDiskSafes()

    for safe in safes:
        if description == safe.description:
            return safe
    return None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True),
            password=dict(required=True),
            description=dict(required=True),
            agent=dict(required=True),
            path=dict(required=True, type='path')
        ),
        supports_check_mode=True
    )

    agent = module.params.get('agent')
    description = module.params.get('description')
    path = module.params.get('path')
    username = module.params.get('username')
    password = module.params.get('password')

    http_auth = HTTPBasicAuth(username, password)
    transport = Transport(http_auth=http_auth)
    client = Client('http://localhost:9080/DiskSafe?wsdl', transport=transport)

    # Lookup the agent by hostname
    agent = _get_agent(transport, agent)
    if agent is None:
        module.fail_json(msg='Agent missing from server')

    # Lookup the disk safe
    disk_safe = _get_disk_safe(client, description)
    if disk_safe:
        module.exit_json(changed=False)

    # Not check mode, create the disk safe
    if not module.check_mode:
        disk_safe = {
            'description': description,
            'path': path,
            'compressionType': 'QUICKLZ',
            'deviceBackupType': 'AUTO_ADD_DEVICES',
            'backupPartitionTable': True,
            'agentID': agent['id']
        }

        try:
            client.service.createDiskSafeWithObject(disksafe=disk_safe)
        except (Fault, ValueError) as ex:
            module.fail_json(msg=ex.message)

    # New volume created!
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
