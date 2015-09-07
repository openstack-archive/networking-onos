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

import mock
import requests

from oslo_config import cfg
from oslo_serialization import jsonutils
from oslotest import base

from neutron.common import constants as n_const
from neutron.plugins.common import constants
from neutron.plugins.ml2 import driver_api as api
from neutron.plugins.ml2 import driver_context as ctx

import networking_onos.plugins.ml2.driver as onos_ml2_driver


fake_network_uuid = 'd897e21a-dfd6-4331-a5dd-7524fa421c3e'
fake_network_object = {'status': 'ACTIVE',
                       'subnets': [],
                       'name': 'net1',
                       'provider:physical_network': None,
                       'admin_state_up': True,
                       'tenant_id': 'test-tenant',
                       'provider:network_type': 'local',
                       'router:external': False,
                       'shared': False,
                       'id': fake_network_uuid,
                       'provider:segmentation_id': None}

fake_subnet_uuid = 'd897e21a-dfd6-4331-a5dd-7524fa421c3e'
fake_subnet_object = {'ipv6_ra_mode': None,
                      'allocation_pools': [{'start': '10.0.0.2',
                                            'end': '10.0.1.254'}],
                      'host_routes': [],
                      'ipv6_address_mode': None,
                      'cidr': '10.0.0.0/23',
                      'id': fake_subnet_uuid,
                      'name': '',
                      'enable_dhcp': True,
                      'network_id': fake_network_uuid,
                      'tenant_id': 'test-tenant',
                      'dns_nameservers': [],
                      'gateway_ip': '10.0.0.1',
                      'ip_version': 4,
                      'shared': False}

fake_port_uuid = '72c56c48-e9b8-4dcf-b3a7-0813bb3bd839'
fake_port_object = {'status': 'DOWN',
                    'binding:host_id': '',
                    'allowed_address_pairs': [],
                    'device_owner': 'fake_owner',
                    'binding:profile': {},
                    'fixed_ips': [],
                    'id': fake_port_uuid,
                    'security_groups':
                    ['2f9244b4-9bee-4e81-bc4a-3f3c2045b3d7'],
                    'device_id': 'fake_device',
                    'name': '',
                    'admin_state_up': True,
                    'network_id': fake_network_uuid,
                    'tenant_id': 'test-tenant',
                    'binding:vif_details': {},
                    'binding:vnic_type': 'normal',
                    'binding:vif_type': 'unbound',
                    'mac_address': '12:34:56 :78:21:b6'}


class ONOSMechanismDriverTestCase(base.BaseTestCase,
                                  onos_ml2_driver.ONOSMechanismDriver):

    def setUp(self):
        super(ONOSMechanismDriverTestCase, self).setUp()
        self.set_test_config()

    def set_test_config(self):
        cfg.CONF.set_override('url_path', 'http://127.0.0.1:1111', 'onos')
        cfg.CONF.set_override('username', 'onos_user', 'onos')
        cfg.CONF.set_override('password', 'awesome', 'onos')
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username,
                          cfg.CONF.onos.password)

    def _mock_req_resp(self, status_code):
        response = mock.Mock(status_code=status_code)
        response.raise_for_status = mock.Mock()
        return response

    def _test_response(self, context, oper_type, obj_type, mock_method):
        body = None
        if oper_type is not 'delete':
            entity = {obj_type: context.current.copy()}
            body = jsonutils.dumps(entity, indent=2)
        if oper_type == 'post':
            url = '%s/%s' % (self.onos_path, obj_type + 's')
        else:
            url = '%s/%s/%s' % (self.onos_path, obj_type + 's',
                                context.current['id'])
        kwargs = {'url': url, 'data': body}
        mock_method.assert_called_once_with(
            method=oper_type,
            headers={'Content-Type': 'application/json'},
            auth=self.onos_auth, **kwargs)

    def test_create_network_postcommit(self):
        context = mock.Mock(current=fake_network_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.create_network_postcommit(context)
            self._test_response(context, 'post', 'network', mock_method)

    def test_update_network_postcommit(self):
        context = mock.Mock(current=fake_network_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.update_network_postcommit(context)
            self._test_response(context, 'put', 'network', mock_method)

    def test_delete_network_postcommit(self):
        context = mock.Mock(current={'id': fake_network_uuid})
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.delete_network_postcommit(context)
            self._test_response(context, 'delete', 'network', mock_method)

    def test_create_subnet_postcommit(self):
        context = mock.Mock(current=fake_subnet_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.create_subnet_postcommit(context)
            self._test_response(context, 'post', 'subnet', mock_method)

    def test_update_subnet_postcommit(self):
        context = mock.Mock(current=fake_subnet_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.update_subnet_postcommit(context)
            self._test_response(context, 'put', 'subnet', mock_method)

    def test_delete_subnet_postcommit(self):
        context = mock.Mock(current={'id': fake_subnet_uuid})
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.delete_subnet_postcommit(context)
            self._test_response(context, 'delete', 'subnet', mock_method)

    def test_create_port_postcommit(self):
        context = mock.Mock(current=fake_port_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.create_port_postcommit(context)
            self._test_response(context, 'post', 'port', mock_method)

    def test_update_port_postcommit(self):
        context = mock.Mock(current=fake_port_object)
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.update_port_postcommit(context)
            self._test_response(context, 'put', 'port', mock_method)

    def test_delete_port_postcommit(self):
        context = mock.Mock(current={'id': fake_port_uuid})
        resp = self._mock_req_resp(requests.codes.created)
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.delete_port_postcommit(context)
            self._test_response(context, 'delete', 'port', mock_method)

    # given valid  and invalid segments
    valid_segment = {
        api.ID: 'API_ID',
        api.NETWORK_TYPE: constants.TYPE_LOCAL,
        api.SEGMENTATION_ID: 'API_SEGMENTATION_ID',
        api.PHYSICAL_NETWORK: 'API_PHYSICAL_NETWORK'}

    invalid_segment = {
        api.ID: 'API_ID',
        api.NETWORK_TYPE: constants.TYPE_NONE,
        api.SEGMENTATION_ID: 'API_SEGMENTATION_ID',
        api.PHYSICAL_NETWORK: 'API_PHYSICAL_NETWORK'}

    def test_check_segment(self):
        """Validate the check_segment method."""

        # given driver and all network types
        all_network_types = [constants.TYPE_FLAT, constants.TYPE_GRE,
                             constants.TYPE_LOCAL, constants.TYPE_VXLAN,
                             constants.TYPE_VLAN, constants.TYPE_NONE]

        # when checking segments network type
        valid_types = {network_type
                       for network_type in all_network_types
                       if self.check_segment({api.NETWORK_TYPE: network_type})}

        # then true is returned only for valid network types
        self.assertEqual({constants.TYPE_LOCAL, constants.TYPE_GRE,
                          constants.TYPE_VXLAN, constants.TYPE_VLAN},
                         valid_types)

    def test_bind_port(self):
        self.vif_type = "MY_VIF_TYPE"
        self.vif_details = "MY_VIF_DETAILS"
        network = mock.MagicMock(spec=api.NetworkContext)
        port_context = mock.MagicMock(
            spec=ctx.PortContext, current={'id': 'CURRENT_CONTEXT_ID'},
            segments_to_bind=[self.valid_segment, self.invalid_segment],
            network=network)

        # when port is bound
        self.bind_port(port_context)

        # then context binding is setup with returned vif_type and valid
        # segment api ID
        port_context.set_binding.assert_called_once_with(
            self.valid_segment[api.ID], self.vif_type,
            self.vif_details, status=n_const.PORT_STATUS_ACTIVE)
