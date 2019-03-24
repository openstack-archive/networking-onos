..
      Copyright 2015-2016 Huawei India Pvt Ltd. All rights reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.


      Convention for heading levels in Neutron devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

Service Function Chaining
-------------------------
ONOS implements `networking-sfc's port-chain api's
<https://github.com/openstack/networking-sfc/blob/master/doc/source/api.rst>`_
for realizing service function chaining.

Mode of Working
~~~~~~~~~~~~~~~
networking-onos provides a shim layer between ONOS and networking-sfc to
realize service function chaining in ONOS. This shim layer makes the
communication between ONOS and networking-sfc possible via ReST calls.

Usage
~~~~~
To use networking-onos SFC driver below steps needs to be followed:

Manual method
+++++++++++++
1. Download and install networking-onos.

2. Download and install networking-sfc.

3. Enable Sfc service plugin in neutron.

Devstack method
+++++++++++++++
1. Update [[local|localrc]] with
   ::

     enable_plugin networking-sfc https://git.openstack.org/openstack/networking-sfc
     enable_plugin networking-onos https://git.openstack.org/openstack/networking-onos

3. run ./stack.sh

Code
~~~~
https://github.com/openstack/networking-onos/blob/master/networking_onos/services/sfc/driver.py
