# Copyright (c) 2016 Huawei Technologies India Pvt Ltd
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

import copy
import mock
from webob import exc

from oslo_utils import uuidutils

from neutron.tests.unit.api.v2 import test_base
from neutron.tests.unit.extensions import base as test_ext

from networking_sfc.extensions import sfc as sfc_ext

_uuid = uuidutils.generate_uuid
_get_path = test_base._get_path

PORT_CHAIN_PATH = (sfc_ext.SFC_PREFIX[1:] + '/port_chains')
PORT_PAIR_PATH = (sfc_ext.SFC_PREFIX[1:] + '/port_pairs')
PORT_PAIR_GROUP_PATH = (sfc_ext.SFC_PREFIX[1:] + '/port_pair_groups')
fmt = 'json'


class OnosSfcDriverTestCase(test_ext.ExtensionTestCase):
    def setUp(self):
        super(OnosSfcDriverTestCase, self).setUp()
        self._setUpExtension(
            'networking_sfc.extensions.sfc.SfcPluginBase',
            sfc_ext.SFC_EXT,
            sfc_ext.RESOURCE_ATTRIBUTE_MAP,
            sfc_ext.Sfc,
            sfc_ext.SFC_PREFIX[1:],
            plural_mappings={}
        )
        self.instance = self.plugin.return_value

    def _get_expected_port_chain(self, data):
        return {'port_chain': {
            'description': data['port_chain'].get('description') or '',
            'name': data['port_chain'].get('name') or '',
            'port_pair_groups': data['port_chain']['port_pair_groups'],
            'chain_parameters': data['port_chain'].get(
                'chain_parameters') or {'correlation': 'mpls'},
            'flow_classifiers': data['port_chain'].get(
                'flow_classifiers') or [],
            'tenant_id': data['port_chain']['tenant_id']
        }}

    def test_create_port_chain(self):
        portchain_id = _uuid()
        data = {'port_chain': {
            'port_pair_groups': [_uuid()],
            'tenant_id': _uuid()
        }}
        expected_data = self._get_expected_port_chain(data)
        return_value = copy.copy(expected_data['port_chain'])
        return_value.update({'id': portchain_id})
        self.instance.create_port_chain.return_value = return_value
        res = self.api.post(_get_path(PORT_CHAIN_PATH, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_port_chain.assert_called_with(
            mock.ANY,
            port_chain=expected_data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('port_chain', res)
        self.assertEqual(return_value, res['port_chain'])

    def test_port_chain_update(self):
        portchain_id = _uuid()
        update_data = {'port_chain': {
            'name': 'new_name',
            'description': 'new_desc',
            'flow_classifiers': [_uuid()]
        }}
        return_value = {
            'tenant_id': _uuid(),
            'id': portchain_id
        }
        self.instance.update_port_chain.return_value = return_value
        res = self.api.put(_get_path(PORT_CHAIN_PATH, id=portchain_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))
        self.instance.update_port_chain.assert_called_with(
            mock.ANY, portchain_id,
            port_chain=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('port_chain', res)
        self.assertEqual(res['port_chain'], return_value)

    def test_port_chain_delete(self):
        self._test_entity_delete('port_chain')

    def _get_expected_port_pair_group(self, data):
        return {'port_pair_group': {
            'description': data['port_pair_group'].get('description') or '',
            'name': data['port_pair_group'].get('name') or '',
            'port_pairs': data['port_pair_group'].get('port_pairs') or [],
            'tenant_id': data['port_pair_group']['tenant_id']
        }}

    def test_create_port_pair_group(self):
        portpairgroup_id = _uuid()
        data = {'port_pair_group': {
            'tenant_id': _uuid()
        }}
        expected_data = self._get_expected_port_pair_group(data)
        return_value = copy.copy(expected_data['port_pair_group'])
        return_value.update({'id': portpairgroup_id})
        self.instance.create_port_pair_group.return_value = return_value
        res = self.api.post(
            _get_path(PORT_PAIR_GROUP_PATH, fmt=self.fmt),
            self.serialize(data),
            content_type='application/%s' % self.fmt)
        self.instance.create_port_pair_group.assert_called_with(
            mock.ANY,
            port_pair_group=expected_data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('port_pair_group', res)
        self.assertEqual(return_value, res['port_pair_group'])

    def test_port_pair_group_update(self):
        portpairgroup_id = _uuid()
        update_data = {'port_pair_group': {
            'name': 'new_name',
            'description': 'new_desc',
            'port_pairs': [_uuid()]
        }}
        return_value = {
            'tenant_id': _uuid(),
            'id': portpairgroup_id
        }
        self.instance.update_port_pair_group.return_value = return_value
        res = self.api.put(
            _get_path(
                PORT_PAIR_GROUP_PATH, id=portpairgroup_id,
                fmt=self.fmt),
            self.serialize(update_data))
        self.instance.update_port_pair_group.assert_called_with(
            mock.ANY, portpairgroup_id,
            port_pair_group=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('port_pair_group', res)
        self.assertEqual(res['port_pair_group'], return_value)

    def test_port_pair_group_delete(self):
        self._test_entity_delete('port_pair_group')

    def _get_expected_port_pair(self, data):
        return {'port_pair': {
            'name': data['port_pair'].get('name') or '',
            'description': data['port_pair'].get('description') or '',
            'ingress': data['port_pair']['ingress'],
            'egress': data['port_pair']['egress'],
            'service_function_parameters': data['port_pair'].get(
                'service_function_parameters') or {'correlation': None},
            'tenant_id': data['port_pair']['tenant_id']
        }}

    def test_create_port_pair(self):
        portpair_id = _uuid()
        data = {'port_pair': {
            'ingress': _uuid(),
            'egress': _uuid(),
            'tenant_id': _uuid()
        }}
        expected_data = self._get_expected_port_pair(data)
        return_value = copy.copy(expected_data['port_pair'])
        return_value.update({'id': portpair_id})
        self.instance.create_port_pair.return_value = return_value
        res = self.api.post(_get_path(PORT_PAIR_PATH, fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        self.instance.create_port_pair.assert_called_with(
            mock.ANY,
            port_pair=expected_data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('port_pair', res)
        self.assertEqual(return_value, res['port_pair'])

    def test_port_pair_update(self):
        portpair_id = _uuid()
        update_data = {'port_pair': {
            'name': 'new_name',
            'description': 'new_desc'
        }}
        return_value = {
            'tenant_id': _uuid(),
            'id': portpair_id
        }
        self.instance.update_port_pair.return_value = return_value
        res = self.api.put(_get_path(PORT_PAIR_PATH, id=portpair_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        self.instance.update_port_pair.assert_called_with(
            mock.ANY, portpair_id,
            port_pair=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('port_pair', res)
        self.assertEqual(res['port_pair'], return_value)

    def test_port_pair_delete(self):
        self._test_entity_delete('port_pair')
