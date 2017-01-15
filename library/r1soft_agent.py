#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport


def _agent_exists(client, hostname):
    agents = client.service.getAgents()

    for agent in agents:
        if hostname == agent.hostname:
            return True
    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True),
            password=dict(required=True),
            hostname=dict(required=True),
            port=dict(required=True, type='int'),
            description=dict()
        ),
        supports_check_mode=True
    )

    hostname = module.params.get('hostname')
    port = module.params.get('port')
    description = module.params.get('description')
    username = module.params.get('username')
    password = module.params.get('password')

    http_auth = HTTPBasicAuth(username, password)
    transport = Transport(http_auth=http_auth)
    client = Client('http://localhost:9080/Agent?wsdl', transport=transport)

    # Volume already exists
    if _agent_exists(client, hostname):
        module.exit_json(changed=False)

    # Not check mode, create the volume
    if not module.check_mode:
        try:
            client.service.createAgent(hostname=hostname, portNumber=port,
                                       description=description)
        except Fault as ex:
            module.fail_json(msg=ex.message)

    # New volume created!
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
