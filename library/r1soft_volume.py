#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport


def _volume_exists(client, path):
    volumes = client.service.getVolumes()

    for vol in volumes:
        if path == vol.path:
            return True
    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True),
            password=dict(required=True),
            name=dict(required=True),
            description=dict(),
            path=dict(required=True, type='path')
        ),
        supports_check_mode=True
    )

    name = module.params.get('name')
    description = module.params.get('description')
    path = module.params.get('path')
    username = module.params.get('username')
    password = module.params.get('password')

    http_auth = HTTPBasicAuth(username, password)
    transport = Transport(http_auth=http_auth)
    client = Client('http://localhost:9080/Volume?wsdl', transport=transport)

    # Volume already exists
    if _volume_exists(client, path):
        module.exit_json(changed=False)

    # Not check mode, create the volume
    if not module.check_mode:
        try:
            client.service.createVolume(name=name, description=description,
                                        path=path, quotaType='NONE')
        except Fault as ex:
            module.fail_json(msg=ex.message)

    # New volume created!
    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
