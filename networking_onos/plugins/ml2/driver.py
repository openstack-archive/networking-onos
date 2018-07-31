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


class ONOSMechanismDriver(api.MechanismDriver):

    """Open Networking Operating System ML2 Driver for Neutron.

    Code which makes communication between ONOS and OpenStack Neutron
    possible.
    """
    def __init__(self,
                 vif_details={portbindings.CAP_PORT_FILTER: False},
                 supported_vnic_types=[portbindings.VNIC_NORMAL,
                                       portbindings.VNIC_DIRECT]):
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)
        self.vif_details = vif_details
        self.supported_vnic_types = supported_vnic_types
        self.vnic_type_for_vif_type = (
            {vtype: portbindings.VIF_TYPE_HW_VEB
                if vtype == portbindings.VNIC_DIRECT
                else portbindings.VIF_TYPE_OVS
             for vtype in self.supported_vnic_types})

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
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {'port': resource})

    @log_helpers.log_method_call
    def delete_port_postcommit(self, context):
        entity_path = 'ports/' + context.current['id']
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)

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

    @log_helpers.log_method_call
    def check_segment(self, segment):
        """Check whether segment is valid for the ONOS MechanismDriver."""

        return segment[api.NETWORK_TYPE] in [n_const.TYPE_LOCAL,
                                             n_const.TYPE_GRE,
                                             n_const.TYPE_VXLAN,
                                             n_const.TYPE_VLAN,
                                             n_const.TYPE_FLAT]
