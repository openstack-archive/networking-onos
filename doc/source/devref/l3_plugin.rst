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

L3 Plugin
---------
networking-onos provides a shim layer between ONOS and Neutron's L3 framework
to realize neutron's layer 3 functionality in ONOS. This shim layer makes the
communication between ONOS and networking-sfc possible via ReST calls.

Mode of Working
~~~~~~~~~~~~~~~
networking-onos.plugins.l3 provides a shim layer between ONOS and neutron for
realizing neutron's router functionality in ONOS. This shim layer makes the
communication between ONOS and OpenStack neutron possible via ReST calls.

Usage
~~~~~
To use networking-onos L3 Plugin functionality, one should

1. Install networking-onos.

2. Configure ONOS as the required L3 service plugin in "neutron.conf"::

    service_plugins = networking_onos.plugins.l3.driver:ONOSL3Plugin

3. Configure ONOS credentials in networking_onos/etc/conf_onos.ini.

4. Start neutron server mentioning networking_onos/etc/conf_onos.ini as one of the config-file.

Code
~~~~
https://github.com/openstack/networking-onos/tree/master/networking_onos/plugins/l3/driver.py
