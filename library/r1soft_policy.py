#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport


def _get_disk_safe(transport, description):
    client = Client('http://localhost:9080/DiskSafe?wsdl', transport=transport)
    safes = client.service.getDiskSafes()

    for safe in safes:
        if description == safe['description']:
            return safe
    return None


def _get_policy(client, name):
    policies = client.service.getPolicies()

    for policy in policies:
        if name == policy['name']:
            return policy
    return None


def camel(chars):
    """ Convert word to camel case """
    words = chars.split('_')
    return "".join(w.lower() if i is 0 else w.title() for i, w in enumerate(words))


def _generate_frequency_values(data):
    return {
        camel(k): v
        for k, v in data.iteritems()
    }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True),
            password=dict(required=True),
            name=dict(required=True),
            description=dict(required=False),
            disk_safe=dict(required=True),
            replication_frequency=dict(required=True, type='dict'),
            merge_frequency=dict(required=True, type='dict'),
            databases=dict(required=False, default=[], type='list')
        ),
        supports_check_mode=True
    )

    username = module.params.get('username')
    password = module.params.get('password')
    http_auth = HTTPBasicAuth(username, password)
    transport = Transport(http_auth=http_auth)
    client = Client('http://localhost:9080/Policy2?wsdl', transport=transport)

    # Lookup the disk safe
    disk_safe_name = module.params.get('disk_safe')
    disk_safe = _get_disk_safe(transport, disk_safe_name)
    if not disk_safe:
        module.fail_json(msg="Could not find disk safe: %s" % disk_safe_name)

    # Lookup the policy
    name = module.params.get('name')
    policy = _get_policy(client, name)
    if policy:
        module.exit_json(changed=False)

    # Not check mode, create the policy
    if not module.check_mode:
        policy = {
            'name': module.params['name'],
            'description': module.params['description'],
            'diskSafeID': disk_safe['id'],
            'replicationScheduleFrequencyType': module.params['replication_frequency']['type'].upper(),
            'replicationScheduleFrequencyValues': _generate_frequency_values(module.params['replication_frequency'].get('values', {})),
            'mergeScheduleFrequencyType': module.params['merge_frequency']['type'].upper(),
            'mergeScheduleFrequencyValues': _generate_frequency_values(module.params['merge_frequency'].get('values', {})),
            'databaseInstanceList': [
                {
                    'dataBaseType': database['type'].upper(),
                    'name': database['name'],
                    'username': database['username'],
                    'password': database['password'],
                    'portNumber': database['port']
                }
                for database in module.params['databases']
            ]
        }

        try:
            client.service.createPolicy(policy=policy)
        except (Fault, ValueError) as ex:
            module.fail_json(msg=ex.message)

    # New volume created!
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
