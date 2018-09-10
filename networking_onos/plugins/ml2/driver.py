# Copyright (c) 2015 Huawei Technologies India Pvt Ltd
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from neutron_lib.api.definitions import portbindings
from neutron_lib import constants as n_const
from neutron_lib.plugins.ml2 import api

from networking_onos.extensions import securitygroup

from networking_onos.common import config  # noqa
from networking_onos.common import utils as onos_utils

LOG = logging.getLogger(__name__)
DEFAULT_VLAN_ID = 0
VHOST_USER_SOCKET_DIR = '/var/run/openvswitch'
OVS_DATAPATH_NETDEV = 'netdev'
OVS_BRIDGE_BR_INT = 'br-int'


class ONOSMechanismDriver(api.MechanismDriver):

    """Open Networking Operating System ML2 Driver for Neutron.

    Code which makes communication between ONOS and OpenStack Neutron
    possible.
    """
    def __init__(self,
                 vif_details={portbindings.CAP_PORT_FILTER: False},
                 supported_vnic_types=[portbindings.VNIC_NORMAL,
                                       portbindings.VNIC_DIRECT,
                                       portbindings.VNIC_DIRECT_PHYSICAL]):
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)
        self.vif_details = vif_details
        self.supported_vnic_types = supported_vnic_types
        self.vnic_type_for_vif_type = {}
        self.vnic_type_for_vif_type[
            portbindings.VNIC_NORMAL] = portbindings.VIF_TYPE_OVS
        self.vnic_type_for_vif_type[
            portbindings.VNIC_DIRECT] = portbindings.VIF_TYPE_HW_VEB

        self.direct_physical = portbindings.VNIC_DIRECT_PHYSICAL
        self.host_dev = portbindings.VIF_TYPE_HOSTDEV_PHY
        self.vnic_type_for_vif_type[self.direct_physical] = self.host_dev
        self.dpdk_port_vif_type = {}
        self.socket_directory = {}

    def initialize(self):
        LOG.debug("Initializing security group handler")
        sgDriver = securitygroup.SecurityGroupDriver()
        sgDriver.initialize()

    @log_helpers.log_method_call
    def create_network_postcommit(self, context):
        entity_path = 'networks'
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {'network': resource})

    @log_helpers.log_method_call
    def update_network_postcommit(self, context):
        entity_path = 'networks/' + context.current['id']
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {'network': resource})

    @log_helpers.log_method_call
    def delete_network_postcommit(self, context):
        entity_path = 'networks/' + context.current['id']
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)

    @log_helpers.log_method_call
    def create_subnet_postcommit(self, context):
        entity_path = 'subnets'
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {'subnet': resource})

    @log_helpers.log_method_call
    def update_subnet_postcommit(self, context):
        entity_path = 'subnets/' + context.current['id']
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {'subnet': resource})

    @log_helpers.log_method_call
    def delete_subnet_postcommit(self, context):
        entity_path = 'subnets/' + context.current['id']
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)

    @log_helpers.log_method_call
    def create_port_postcommit(self, context):
        entity_path = 'ports'
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {'port': resource})

    @log_helpers.log_method_call
    def update_port_postcommit(self, context):
        entity_path = 'ports/' + context.current['id']
        resource = context.current.copy()
        resp = onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                                   entity_path, {'port': resource})
        port_id = context.current['id']

        """In case of netdev bridge, ONOS sends vif_type with vhostuser"""
        if resp is not None and isinstance(resp, dict):
            if 'vif_type' in resp and not (port_id in self.dpdk_port_vif_type):
                    LOG.debug("vif_type for dpdk port (%(port)s) is (%(vif)s)",
                              {'port': port_id,
                               'vif': resp['vif_type']})
                    self.dpdk_port_vif_type[port_id] = resp['vif_type']
            if 'socket_dir' in resp and not (port_id in self.socket_directory):
                LOG.debug("socket_dir for dpdk port (%(port)s) is (%(dir)s)",
                          {'port': port_id,
                           'dir': resp['socket_dir']})
                self.socket_directory[port_id] = resp['socket_dir']

    @log_helpers.log_method_call
    def delete_port_postcommit(self, context):
        entity_path = 'ports/' + context.current['id']
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)
        port_id = context.current['id']
        if port_id in self.dpdk_port_vif_type:
            del self.dpdk_port_vif_type[port_id]
        if port_id in self.socket_directory:
            del self.socket_directory[port_id]

    @log_helpers.log_method_call
    def bind_port(self, context):
        """Set port binding data for use with nova."""
        LOG.debug("Attempting to bind port %(port)s on network %(network)s",
                  {'port': context.current['id'],
                   'network': context.network.current['id']})
        # Prepared porting binding data
        vnic_type = context.current.get(portbindings.VNIC_TYPE,
                                        portbindings.VNIC_NORMAL)
        if vnic_type not in self.supported_vnic_types:
            LOG.debug("Refusing to bind due to unsupported vnic_type: %s",
                      vnic_type)
            return

        for segment in context.segments_to_bind:
            if self.check_segment(segment):
                if context.current['id'] in self.dpdk_port_vif_type:
                    context.set_binding(segment[api.ID],
                                        portbindings.VIF_TYPE_VHOST_USER,
                                        self.get_vhost_user_vif_details(
                                            context),
                                        status=n_const.PORT_STATUS_ACTIVE)
                else:
                    vif_type = self.vnic_type_for_vif_type.get(
                        vnic_type, portbindings.VIF_TYPE_OVS)
                    context.set_binding(segment[api.ID],
                                        vif_type,
                                        self._get_vif_details(segment),
                                        status=n_const.PORT_STATUS_ACTIVE)
                LOG.debug("Port bound successful for segment: %s", segment)
                return
            else:
                LOG.debug("Port bound un-successful for segment ID %(id)s, "
                          "segment %(seg)s, phys net %(physnet)s, and "
                          "network type %(nettype)s",
                          {'id': segment[api.ID],
                           'seg': segment[api.SEGMENTATION_ID],
                           'physnet': segment[api.PHYSICAL_NETWORK],
                           'nettype': segment[api.NETWORK_TYPE]})

    def _get_vif_details(self, segment):
        network_type = segment[api.NETWORK_TYPE]
        vif_details = self.vif_details.copy()

        if network_type == n_const.TYPE_VLAN:
            vlan_id = segment[api.SEGMENTATION_ID]
            vif_details[portbindings.VIF_DETAILS_VLAN] = str(vlan_id)
        else:
            vlan_id = DEFAULT_VLAN_ID
            vif_details[portbindings.VIF_DETAILS_VLAN] = str(vlan_id)

        return vif_details

    def get_vhost_user_vif_details(self, context):
        mode = portbindings.VHOST_USER_MODE_SERVER
        sockdir = VHOST_USER_SOCKET_DIR
        port_id = context.current['id']

        if port_id in self.socket_directory:
            sockdir = self.socket_directory[port_id]

        sock_name = (n_const.VHOST_USER_DEVICE_PREFIX + port_id)[:14]
        sock_path = os.path.join(sockdir, sock_name)
        details = {portbindings.CAP_PORT_FILTER: False,
                   portbindings.OVS_HYBRID_PLUG: False,
                   portbindings.VHOST_USER_MODE: mode,
                   portbindings.VHOST_USER_OVS_PLUG: True,
                   portbindings.VHOST_USER_SOCKET: sock_path,
                   portbindings.OVS_DATAPATH_TYPE: OVS_DATAPATH_NETDEV,
                   portbindings.VIF_DETAILS_BRIDGE_NAME: OVS_BRIDGE_BR_INT}
        return details

    @log_helpers.log_method_call
    def check_segment(self, segment):
        """Check whether segment is valid for the ONOS MechanismDriver."""

        return segment[api.NETWORK_TYPE] in [n_const.TYPE_LOCAL,
                                             n_const.TYPE_GRE,
                                             n_const.TYPE_VXLAN,
                                             n_const.TYPE_VLAN,
                                             n_const.TYPE_FLAT]
