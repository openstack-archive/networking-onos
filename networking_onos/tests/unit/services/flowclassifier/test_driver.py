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

from networking_sfc.extensions import flowclassifier as fc_ext

_uuid = uuidutils.generate_uuid
_get_path = test_base._get_path

FLOW_CLASSIFIER_PATH = (fc_ext.FLOW_CLASSIFIER_PREFIX[1:] + '/' +
                        fc_ext.FLOW_CLASSIFIER_EXT + 's')
fmt = 'json'


class OnosFlowClassifierDriverTestCase(test_ext.ExtensionTestCase):

    def setUp(self):
        super(OnosFlowClassifierDriverTestCase, self).setUp()
        self._setUpExtension(
            'networking_sfc.extensions.flowclassifier.'
            'FlowClassifierPluginBase',
            fc_ext.FLOW_CLASSIFIER_EXT,
            fc_ext.RESOURCE_ATTRIBUTE_MAP,
            fc_ext.Flowclassifier,
            fc_ext.FLOW_CLASSIFIER_PREFIX[1:],
            plural_mappings={}
        )
        self.instance = self.plugin.return_value

    def _get_expected_flow_classifier(self, data):
        source_port_range_min = data['flow_classifier'].get(
            'source_port_range_min')
        if source_port_range_min is not None:
            source_port_range_min = int(source_port_range_min)
        source_port_range_max = data['flow_classifier'].get(
            'source_port_range_max')
        if source_port_range_max is not None:
            source_port_range_max = int(source_port_range_max)
        destination_port_range_min = data['flow_classifier'].get(
            'destination_port_range_min')
        if destination_port_range_min is not None:
            destination_port_range_min = int(destination_port_range_min)
        destination_port_range_max = data['flow_classifier'].get(
            'destination_port_range_max')
        if destination_port_range_max is not None:
            destination_port_range_max = int(destination_port_range_max)

        return {'flow_classifier': {
            'name': data['flow_classifier'].get('name') or '',
            'description': data['flow_classifier'].get('description') or '',
            'tenant_id': data['flow_classifier']['tenant_id'],
            'source_port_range_min': source_port_range_min,
            'source_port_range_max': source_port_range_max,
            'destination_port_range_min': destination_port_range_min,
            'destination_port_range_max': destination_port_range_max,
            'l7_parameters': data['flow_classifier'].get(
                'l7_parameters') or {},
            'destination_ip_prefix': data['flow_classifier'].get(
                'destination_ip_prefix'),
            'source_ip_prefix': data['flow_classifier'].get(
                'source_ip_prefix'),
            'logical_source_port': data['flow_classifier'].get(
                'logical_source_port'),
            'logical_destination_port': data['flow_classifier'].get(
                'logical_destination_port'),
            'ethertype': data['flow_classifier'].get(
                'ethertype') or 'IPv4',
            'protocol': data['flow_classifier'].get(
                'protocol')
        }}

    def _clean_expected_flow_classifier(self, expected_flow_classifier):
        if 'logical_source_port' in expected_flow_classifier:
            del expected_flow_classifier['logical_source_port']
        if 'logical_destination_port' in expected_flow_classifier:
            del expected_flow_classifier['logical_destination_port']

    def test_create_flow_classifier(self):
        flowclassifier_id = _uuid()
        data = {'flow_classifier': {
            'logical_source_port': _uuid(),
            'logical_destination_port': _uuid(),
            'tenant_id': _uuid(),
        }}
        expected_data = self._get_expected_flow_classifier(data)
        return_value = copy.deepcopy(expected_data['flow_classifier'])
        return_value.update({'id': flowclassifier_id})
        self._clean_expected_flow_classifier(return_value)
        self.instance.create_flow_classifier.return_value = return_value
        res = self.api.post(
            _get_path(FLOW_CLASSIFIER_PATH, fmt=self.fmt),
            self.serialize(data),
            content_type='application/%s' % self.fmt)
        self.instance.create_flow_classifier.assert_called_with(
            mock.ANY,
            flow_classifier=expected_data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('flow_classifier', res)
        self.assertEqual(return_value, res['flow_classifier'])

    def test_flow_classifier_update(self):
        flowclassifier_id = _uuid()
        update_data = {'flow_classifier': {
            'name': 'new_name',
            'description': 'new_desc',
        }}
        return_value = {
            'tenant_id': _uuid(),
            'id': flowclassifier_id
        }
        self.instance.update_flow_classifier.return_value = return_value

        res = self.api.put(
            _get_path(FLOW_CLASSIFIER_PATH, id=flowclassifier_id,
                      fmt=self.fmt),
            self.serialize(update_data))

        self.instance.update_flow_classifier.assert_called_with(
            mock.ANY, flowclassifier_id,
            flow_classifier=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('flow_classifier', res)
        self.assertEqual(res['flow_classifier'], return_value)

    def test_flow_classifier_delete(self):
        self._test_entity_delete('flow_classifier')
