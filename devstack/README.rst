======================
 Enabling in Devstack
======================

NOTE: ONOS VTN application adds 'eth0' to br-int bridge, so please DON'T use 'eth0'
as your connection point and 'eth0' MUST exist.

1. Download networking-onos devstack

2. Copy the sample local.conf over::

     cp devstack/local.conf.example local.conf

3. Optionally, to manually configure this:

   Add this repo as an external repository::

     > cat local.conf
     [[local|localrc]]
     enable_plugin networking-onos http://git.openstack.org/openstack/networking-onos

4. Optionally, to enable ONOS L3:

   Add this repo as an external repository::

     > cat local.conf
     [[local|localrc]]
     enable_plugin networking-onos http://git.openstack.org/openstack/networking-onos
     ONOS_L3=True

5. run ``stack.sh``

6. Note: In a multi-node devstack environment, for each compute node you will want to add this
   to the local.conf file::

     > cat local.conf
     enable_plugin networking-onos http://git.openstack.org/openstack/networking-onos
     ONOS_MODE=compute
