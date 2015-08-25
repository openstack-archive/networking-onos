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
import networking_onos.plugins.ml2.mech_driver as onos_driver
from oslo_config import cfg
from oslo_serialization import jsonutils
import requests

from networking_onos.tests.unit import base

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


class OnosMechanismDriverTestCase(base.TestCase,
                                  onos_driver.ONOSMechanismDriver):

    def setUp(self):
        super(OnosMechanismDriverTestCase, self).setUp()
        cfg.CONF.set_override('url_path', 'http://127.0.0.1:1111', 'ml2_onos')
        cfg.CONF.set_override('username', 'onos_user', 'ml2_onos')
        cfg.CONF.set_override('password', 'awesome', 'ml2_onos')
        self.onos_path = cfg.CONF.ml2_onos.url_path
        self.onos_auth = (cfg.CONF.ml2_onos.username,
                          cfg.CONF.ml2_onos.password)

    def _mock_req_resp(self, status_code):
        response = mock.Mock(status_code=status_code)
        response.raise_for_status = mock.Mock()
        return response

    def _test_response(self, context, oper_type, obj_type, mock_method):
        body = None
        if oper_type is not 'delete':
            entity = {obj_type: context.current.copy()}
            body = jsonutils.dumps(entity, indent=2)
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
