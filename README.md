R1Soft
======
This role allows you to setup and configure both R1Soft servers and agents.


Requirements
------------
The role currently doesn't cover all of the settings for resources, we have a
few which we've configured with that we believe are the most commonly used
options.  We welcome contributions for changes to specific settings.


Dependencies
------------
This role requires that the Python package `zeep` is installed on the server
in order to be able to make API calls to the R1Soft SOAP API.


Example Playbook
----------------
You can look at the playbook which is used in testing which is located in at
[`tests/test.yml`](tests/test.yml).  In addition, you can also check at the
variables that it uses by looking at the [`molecule.yml`](molecule.yml) file
which is used in testing.


Known Issues
------------
Contributions to solve the following known issues and limitations are more than
welcome!

- This role does not currently support creating volumes with specific quotes,
  they are hard coded to `NONE`.


License
-------
Apache


Author Information
------------------
http://vexxhost.com
