# Copyright (C) 2015 Huawei Technologies India Pvt Ltd.
# All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

import copy
import mock

from oslotest import base

from neutron.extensions import l3
from neutron.tests.unit.api.v2 import test_base
from neutron.tests.unit.extensions import base as test_neutron_extensions
from webob import exc

import networking_onos.plugins.l3.driver as onos_driver

fake_tenant_id = '048aa98a3ec345dc8b14427c81e276cf'

fake_router_uuid = '292f7967-c5e7-47d8-8265-dc2160678b75'
fake_router_object = {'router': {'name': 'router_abc',
                                 'external_gateway_info': None,
                                 'admin_state_up': True,
                                 'tenant_id': fake_tenant_id}}

fake_network_id = '7464aaf0-27ea-448a-97df-51732f9e0e27'
fake_router_external_info = {'external_gateway_info':
                             {'network_id': fake_network_id,
                              'enable_snat': False}}

fake_floating_ip_id = '7464aaf0-27ea-448a-97df-51732f9e0e25'
fake_floating_ip = {'floatingip':
                    {'fixed_ip_address': '10.1.1.1',
                     'id': fake_floating_ip_id,
                     'router_id': fake_router_uuid,
                     'port_id': None,
                     'status': None,
                     'tenant_id': fake_tenant_id}}

fake_port_id = '7db560e9-76d4-4bf9-9c28-43efa7afa45d'
fake_subnet_id = 'dc2b8071-c24c-4a8e-b471-dbf3fbe55830'
fake_port = {'id': fake_port_id,
             'network_id': fake_network_id,
             'fixed_ips': [{'ip_address': '21.41.4.5',
                            'prefixlen': 28,
                            'subnet_id': fake_subnet_id}],
             'subnets': [{'id': fake_subnet_id,
                          'cidr': '21.41.4.0/28',
                          'gateway_ip': '21.41.4.1'}]}

fake_floating_ip_update_info = {'floating_network_id': fake_network_id,
                                'tenant_id': fake_tenant_id,
                                'fixed_ip_address': '20.1.1.11',
                                'subnet_id': fake_port['subnets'][0]['id'],
                                'port_id': fake_port_id,
                                'floating_ip_address': '198.1.2.3'}

fake_interface_add = {'subnet_id': fake_subnet_id}

fake_interface_remove = {'subnet_id': fake_subnet_id,
                         'port_id': fake_port_id}


class ONOSL3PluginTestCase(base.BaseTestCase,
                           test_neutron_extensions.ExtensionTestCase,
                           onos_driver.ONOSL3Plugin):

    def setUp(self):
        super(ONOSL3PluginTestCase, self).setUp()
        self._setUpExtension(
            'neutron.extensions.l3.RouterPluginBase', None,
            l3.RESOURCE_ATTRIBUTE_MAP, l3.L3, None,
            allow_pagination=True, allow_sorting=True,
            supported_extension_aliases=['router'],
            use_quota=True)
        self.instance = self.plugin.return_value

    def _mock_req_res(self, status_code):
        response = mock.Mock(status_code=status_code)
        response.raise_for_status = mock.Mock()
        return response

    def _test_send_msg(self, dict_info, oper_type, url):
        if oper_type == 'post':
            resp = self.api.post(url, self.serialize(dict_info))
        elif oper_type == 'put':
            resp = self.api.put(url, self.serialize(dict_info))
        else:
            resp = self.api.delete(url)
        return resp

    def test_create_router(self):
        router_info = copy.deepcopy(fake_router_object['router'])
        router_info.update({'status': 'ACTIVE', 'id': fake_router_uuid})
        self.instance.create_router.return_value = router_info
        self.instance.get_routers_count.return_value = 0
        url = test_base._get_path('routers', fmt=self.fmt)
        resp = self._test_send_msg(fake_router_object, 'post', url)
        self.instance.create_router.\
            assert_called_once_with(mock.ANY, router=fake_router_object)
        self._verify_resp(resp, exc.HTTPCreated.code,
                          'router', fake_router_uuid)

    def test_update_router(self):
        router_info = copy.deepcopy(fake_router_object['router'])
        router_info.update(fake_router_external_info)
        router_info.update({'status': 'ACTIVE', 'id': fake_router_uuid})
        self.instance.update_router.return_value = router_info
        router_request = {'router': fake_router_external_info}
        url = test_base._get_path('routers', id=fake_router_uuid, fmt=self.fmt)
        resp = self._test_send_msg(router_request, 'put', url)
        self.instance.update_router.\
            assert_called_once_with(mock.ANY, fake_router_uuid,
                                    router=router_request)
        self._verify_resp(resp, exc.HTTPOk.code, 'router', fake_router_uuid)

    def test_delete_router(self):
        url = test_base._get_path('routers', id=fake_router_uuid, fmt=self.fmt)
        resp = self._test_send_msg(None, 'delete', url)
        self.instance.delete_router.assert_called_once_with(mock.ANY,
                                                            fake_router_uuid)
        self.assertEqual(resp.status_int, exc.HTTPNoContent.code)

    def test_create_floating_ip(self):
        floatingip_info = copy.deepcopy(fake_floating_ip['floatingip'])
        floatingip_info.update(fake_floating_ip_update_info)
        floatingip_info.update({'status': 'ACTIVE', 'fixed_ip_address': None})

        self.instance.create_floatingip.return_value = floatingip_info
        self.instance.get_floatingips_count.return_value = 0
        self.instance.get_port = mock.Mock(return_value=fake_port)

        floating_ip_request = {'floatingip': fake_floating_ip_update_info}
        url = test_base._get_path('floatingips', fmt=self.fmt)
        resp = self._test_send_msg(floating_ip_request, 'post', url)
        self.instance.create_floatingip.\
            assert_called_once_with(mock.ANY,
                                    floatingip=floating_ip_request)
        self._verify_resp(resp, exc.HTTPCreated.code,
                          'floatingip', fake_floating_ip_id)

    def test_update_floating_ip(self):
        fake_floating_ip_update_info = {'port_id': None}
        floatingip_info = copy.deepcopy(fake_floating_ip['floatingip'])
        floatingip_info.update(fake_floating_ip_update_info)
        floatingip_info.update({'status': 'ACTIVE',
                                'tenant_id': fake_tenant_id,
                                'floating_network_id': fake_network_id,
                                'fixed_ip_address': None,
                                'floating_ip_address': '172.24.4.228'})

        self.instance.update_floatingip.return_value = floatingip_info
        self.instance.get_port = mock.Mock(return_value=fake_port)
        floating_ip_request = {'floatingip': fake_floating_ip_update_info}
        url = test_base._get_path('floatingips',
                                  id=fake_floating_ip_id, fmt=self.fmt)
        resp = self._test_send_msg(floating_ip_request, 'put', url)
        self.instance.update_floatingip.\
            assert_called_once_with(mock.ANY,
                                    fake_floating_ip_id,
                                    floatingip=floating_ip_request)
        self._verify_resp(resp, exc.HTTPOk.code,
                          'floatingip', fake_floating_ip_id)

    def test_delete_floating_ip(self):
        self.instance.get_port = mock.Mock(return_value=fake_port)
        url = test_base._get_path('floatingips', id=fake_floating_ip_id)
        resp = self._test_send_msg(None, 'delete', url)
        self.instance.delete_floatingip.\
            assert_called_once_with(mock.ANY, fake_floating_ip_id)
        self.assertEqual(resp.status_int, exc.HTTPNoContent.code)

    def test_add_router_interface(self):
        interface_info = {'tenant_id': fake_tenant_id,
                          'port_id': fake_port_id,
                          'id': fake_router_uuid}
        interface_info.update(fake_interface_add)
        self.instance.add_router_interface.return_value = interface_info
        url = test_base._get_path('routers', id=fake_router_uuid,
                                  action='add_router_interface',
                                  fmt=self.fmt)
        resp = self._test_send_msg(fake_interface_add, 'put', url)
        self.instance.add_router_interface.\
            assert_called_once_with(mock.ANY, fake_router_uuid,
                                    fake_interface_add)
        self._verify_resp(resp, exc.HTTPOk.code, None, fake_router_uuid)

    def test_remove_router_interface(self):
        interface_info = {'tenant_id': fake_tenant_id,
                          'id': fake_router_uuid}
        interface_info.update(fake_interface_remove)
        self.instance.remove_router_interface.return_value = interface_info
        url = test_base._get_path('routers', id=fake_router_uuid,
                                  action='remove_router_interface',
                                  fmt=self.fmt)
        resp = self._test_send_msg(fake_interface_remove, 'put', url)
        self.instance.remove_router_interface.\
            assert_called_once_with(mock.ANY, fake_router_uuid,
                                    fake_interface_remove)
        self._verify_resp(resp, exc.HTTPOk.code, None, fake_router_uuid)

    def _verify_resp(self, resp, return_code, context, id):
        self.assertEqual(resp.status_int, return_code)
        resp = self.deserialize(resp)

        if context is None:
            self.assertEqual(resp['id'], id)
            self.assertEqual(resp['subnet_id'], fake_subnet_id)
            return

        self.assertIn(context, resp)
        resource = resp[context]
        self.assertEqual(resource['id'], id)
        if context == 'router':
            self.assertEqual(resource['status'], 'ACTIVE')
            self.assertEqual(resource['admin_state_up'], True)
        elif context == 'floatingip':
            self.assertEqual(resource['status'], 'ACTIVE')
            self.assertEqual(resource['fixed_ip_address'], None)
