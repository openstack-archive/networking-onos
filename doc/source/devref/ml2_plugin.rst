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


ML2 Plugin
----------
networking-onos provides a shim layer between ONOS and Neutron's ML2 framework
to realize neutron's layer 2 network in ONOS. This shim layer makes the
communication between ONOS and networking-sfc possible via ReST calls.

Mode of Working
~~~~~~~~~~~~~~~
The networking-onos project provides a thin layer which makes the communication
between ONOS and OpenStack neutron possible via ReST
call.

Usage
~~~~~
To use networking-onos ML2 Plugin functionality, one should

1. Install networking-onos.

2. Configure ONOS as the required ML2 "mechanism_drivers" in "ml2_conf.ini"::

    mechanism_drivers=onos_ml2

3. Configure ONOS credentials in etc/neutron/plugins/ml2/ml2_conf_onos.ini.

4. Start neutron server mentioning etc/neutron/plugins/ml2/ml2_conf_onos.ini as
one of the config-file.

Code
~~~~
https://github.com/openstack/networking-onos/tree/master/networking_onos/plugins/ml2/driver.py
