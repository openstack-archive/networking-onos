==================================================================
Service Function Chaining Driver for Open Network Operating System
==================================================================

`Blueprint Link
<https://blueprints.launchpad.net/networking-onos/+spec/networking-onos-sfc>`_

This spec implements a OpenStack `networking-sfc <https://wiki.openstack.org/wiki/Neutron/ServiceInsertionAndChaining>`_
driver for Open Network Operating System (ONOS).

Problem Statement
===================

ONOS controller exposes NBI interfaces which allows users to configure and
control network infrastructure layer using different ONOS applications.
`networking-sfc <https://wiki.openstack.org/wiki/Neutron/ServiceInsertionAndChaining>`_
has defined `SFC APIs <https://github.com/openstack/networking-sfc/blob/master/doc/source/api.rst>`_
to realize service function chaining(SFC) functionality. This specification
introduces an networking-sfc driver for carrying SFC API's to ONOS controller.

Proposed Change
===============

This spec implements ONOS driver for `networking-sfc <https://wiki.openstack.org/wiki/Neutron/ServiceInsertionAndChaining>`_
to forwards the API rest calls to ONOS NBIs which is further handled by ONOS
application to generate and download flow rules to the underlying OVS
networking data path to realize SFC functionalities.

Detailed Design
===============

To relaize SFC using ONOS requires specific ONOS controller applications to
receive REST API calls from Openstack and handle them. ONOS SFC driver will act
as a shim layer between OpenStack and ONOS. This shim layer makes the
communication between ONOS and networking-sfc possible via ReST calls.::

                       +------------+   +------------+      +-------------+
                       |            |   |            |      |             |
                       |            |   |            |      |             |
                       | Openstack  |   | ONOS SFC   | ReST |             |
 networking-sfc API----+ Neutron    +---+ Mechanism  +------+  ONOS NBI   |
                       | ML2        |   | Driver     |      |  for SFC    |
                       | Plugin     |   |            |      |             |
                       |            |   |            |      |             |
                       +------------+   +------------+      +-------------+

ONOS NBI will forwards the REST API calls to ONOS application `(VTN) <https://github.com/opennetworkinglab/onos/tree/master/apps/vtn>`_
which will prepare and downloads forwarding behaviour (flow_rules) to all the
OVS along the service chain path. A port chain specifies which port pair group
and flow classifier to use for the chain.

Please refer `sfc driver <https://github.com/openstack/networking-onos/blob/master/doc/source/devref/sfc_driver.rst>`_
and `flowclassifier <https://github.com/openstack/networking-onos/blob/master/doc/source/devref/flowclassifier_driver.rst>`_
for specific driver usage guidelines.

Impact
======
None

Assignee(s)
===========

* Mohan Kumar (nmohankumar1011@gmail.com)
* Vikram Choudhary (vikram.choudhary@huawei.com)

Work Items
----------

1. Add driver 'networking-sfc' for ONOS.
2. Add applicable unit tests.
3. Integrate with networking-sfc port-chain.

References
==========

`[1] https://wiki.openstack.org/wiki/Neutron/ServiceInsertionAndChaining
<https://wiki.openstack.org/wiki/Neutron/ServiceInsertionAndChaining>`_

`[2] https://github.com/openstack/networking-sfc/blob/master/doc/source/api.rst
<https://github.com/openstack/networking-sfc/blob/master/doc/source/api.rst>`_

`[3] https://github.com/openstack/networking-onos/blob/master/doc/source/devref/sfc_driver.rst
<https://github.com/openstack/networking-onos/blob/master/doc/source/devref/sfc_driver.rst>`_

`[4] https://github.com/openstack/networking-onos/blob/master/doc/source/devref/flowclassifier_driver.rst
<https://github.com/openstack/networking-onos/blob/master/doc/source/devref/flowclassifier_driver.rst>`_

`[5] https://github.com/opennetworkinglab/onos/tree/master/apps/vtn
<https://github.com/opennetworkinglab/onos/tree/master/apps/vtn>`_
