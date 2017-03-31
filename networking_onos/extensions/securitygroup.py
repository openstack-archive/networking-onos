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

from oslo_config import cfg
from oslo_log import log as logging


from networking_onos.common import utils as onos_utils
from networking_onos.extensions import callback
from networking_onos.extensions import constant as onos_const

LOG = logging.getLogger(__name__)


class SecurityGroupDriver(object):

    """Open Networking Operating System Security Group Handler for Neutron.

    Allows to forward security group event to ONOS.
    """
    def __init__(self):
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)

    def initialize(self):
        LOG.debug("Initializing the security group callback")
        pre_call = self.sync_from_callback_precommit
        post_call = self.sync_from_callback_postcommit
        self.sg_handler = callback.OnosSecurityGroupHandler(pre_call,
                                                            post_call)

    def sync_from_callback_precommit(self, context, operation, res_type,
                                     res_id, resource_dict):
        pass

    def sync_from_callback_postcommit(self, context, ops, res_type, res_id,
                                      res):
        LOG.debug("sync_from_callback_postcommit is called.")
        if res_type is onos_const.ONOS_SG:
            if ops is onos_const.ONOS_CREATE:
                self.create_security_group_postcommit(context, ops, res_type,
                                                      res_id, res)
            elif ops is onos_const.ONOS_UPDATE:
                self.update_security_group_postcommit(context, ops, res_type,
                                                      res_id, res)
            else:
                self.delete_security_group_postcommit(context, ops, res_type,
                                                      res_id, res)

        elif res_type is onos_const.ONOS_SG_RULE:
            if ops is onos_const.ONOS_CREATE:
                self.create_security_group_rule_postcommit(context, ops,
                                                           res_type, res_id,
                                                           res)
            else:
                self.delete_security_group_rule_postcommit(context, ops,
                                                           res_type, res_id,
                                                           res)

    def create_security_group_postcommit(self, context, ops, res_type, res_id,
                                         res):
        entity_path = 'security-groups'
        onos_utils.send_msg(self.onos_path, self.onos_auth, ops, entity_path,
                            {'security_group': res})

    def update_security_group_postcommit(self, context, ops, res_type, res_id,
                                         res):
        entity_path = 'security-groups/' + res_id
        onos_utils.send_msg(self.onos_path, self.onos_auth, ops, entity_path,
                            {'security_group': res})

    def delete_security_group_postcommit(self, context, ops, res_type, res_id,
                                         res):
        entity_path = 'security-groups/' + res_id
        onos_utils.send_msg(self.onos_path, self.onos_auth, ops, entity_path)

    def create_security_group_rule_postcommit(self, context, ops, res_type,
                                              res_id, res):
        entity_path = 'security-group-rules'
        onos_utils.send_msg(self.onos_path, self.onos_auth, ops, entity_path,
                            {'security_group_rule': res})

    def delete_security_group_rule_postcommit(self, context, ops, res_type,
                                              res_id, res):
        entity_path = 'security-group-rules/' + res_id
        onos_utils.send_msg(self.onos_path, self.onos_auth, ops, entity_path)
