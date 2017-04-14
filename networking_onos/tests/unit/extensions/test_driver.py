# Copyright (c) 2017 SK Telecom Ltd
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

from networking_onos.extensions import constant as onos_const

import networking_onos.extensions.securitygroup as onos_sg_driver


fake_security_group_object_create = {'name': 'new-webservers',
                                     'description':
                                     'security group for webservers'}
fake_security_group_object_update = {'id': '85cc3048-abc3-43cc',
                                     'name': 'new-webservers',
                                     'description': 'security group for web'}
fake_security_group_uuid = '85cc3048-abc3-43cc'
fake_security_group_rule_object = {'direction': 'egress',
                                   'ethertype': 'IPv6',
                                   'id': '3c0e45ff-adaf-4124-b083',
                                   'port_range_max': None,
                                   'port_range_min': None,
                                   'protocol': None,
                                   'remote_group_id': None,
                                   'remote_ip_prefix': None,
                                   'security_group_id': '85cc3048-abc3-43cc',
                                   'project_id': 'e4f50856753b4dc6afee5fa60',
                                   'tenant_id': 'e4f50856753b4dc6afee5fa6b0',
                                   'description': ''}
fake_security_group_rule_uuid = '3c0e45ff-adaf-4124-b083'


class ONOSSecurityGroupTestCase(base.BaseTestCase,
                                onos_sg_driver.SecurityGroupDriver):

    def setUp(self):
        super(ONOSSecurityGroupTestCase, self).setUp()
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

    def _test_response(self, context, oper_type, obj_type, mock_method,
                       uri_path):
        body = None
        if oper_type is not 'delete':
            entity = {obj_type: context.current.copy()}
            body = jsonutils.dumps(entity, indent=2)
        if oper_type == 'post':
            url = '%s/%s' % (self.onos_path, uri_path + 's')
        else:
            url = '%s/%s/%s' % (self.onos_path, uri_path + 's',
                                context.current['id'])
        kwargs = {'url': url, 'data': body}
        mock_method.assert_called_once_with(
            method=oper_type,
            headers={'Content-Type': 'application/json'},
            auth=self.onos_auth, **kwargs)

    def test_create_security_group_postcommit(self):
        context = mock.Mock(current=fake_security_group_object_create)
        resp = self._mock_req_resp(requests.codes.created)
        res = context.current.copy()
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.sync_from_callback_postcommit(context, onos_const.ONOS_CREATE,
                                               onos_const.ONOS_SG, None, res)
            self._test_response(context, 'post', 'security_group', mock_method,
                                'security-group')

    def test_update_security_group_postcommit(self):
        context = mock.Mock(current=fake_security_group_object_update)
        resp = self._mock_req_resp(requests.codes.created)
        res = context.current.copy()
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.sync_from_callback_postcommit(context, onos_const.ONOS_UPDATE,
                                               onos_const.ONOS_SG,
                                               fake_security_group_uuid, res)
            self._test_response(context, 'put', 'security_group', mock_method,
                                'security-group')

    def test_delete_security_group_postcommit(self):
        context = mock.Mock(current={'id': fake_security_group_uuid})
        resp = self._mock_req_resp(requests.codes.created)
        res = context.current.copy()
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.sync_from_callback_postcommit(context, onos_const.ONOS_DELETE,
                                               onos_const.ONOS_SG,
                                               fake_security_group_uuid, res)
            self._test_response(context, 'delete', 'security_group',
                                mock_method, 'security-group')

    def test_create_security_group_rule_postcommit(self):
        context = mock.Mock(current=fake_security_group_rule_object)
        resp = self._mock_req_resp(requests.codes.created)
        res = context.current.copy()
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.sync_from_callback_postcommit(context, onos_const.ONOS_CREATE,
                                               onos_const.ONOS_SG_RULE, None,
                                               res)
            self._test_response(context, 'post', 'security_group_rule',
                                mock_method, 'security-group-rule')

    def test_delete_security_group_rule_postcommit(self):
        context = mock.Mock(current={'id': fake_security_group_rule_uuid})
        resp = self._mock_req_resp(requests.codes.created)
        res = context.current.copy()
        with mock.patch('requests.request',
                        return_value=resp) as mock_method:
            self.sync_from_callback_postcommit(context, onos_const.ONOS_DELETE,
                                               onos_const.ONOS_SG_RULE,
                                               fake_security_group_rule_uuid,
                                               res)
            self._test_response(context, 'delete', 'security_group_rule',
                                mock_method, 'security-group-rule')
