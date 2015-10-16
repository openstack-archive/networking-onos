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

from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from networking_onos.common import config  # noqa
from networking_onos.common import utils as onos_utils

from networking_sfc.services.flowclassifier.drivers import base as fc_driver

LOG = logging.getLogger(__name__)


class OnosFlowClassifierDriver(fc_driver.FlowClassifierDriverBase):

    """Open Networking Operating System SFC Driver for networking-sfc.

    Code which makes communication between ONOS and OpenStack networking-sfc
    possible.
    """
    def __init__(self):
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)

    def initialize(self):
        pass

    @log_helpers.log_method_call
    def create_flow_classifier(self, context):
        entity_path = 'flow_classifiers'
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'post',
                            entity_path, {'flow_classifier': resource})

    @log_helpers.log_method_call
    def update_flow_classifier(self, context):
        entity_path = 'flow_classifiers/' + context.current['id']
        resource = context.current.copy()
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'put',
                            entity_path, {'flow_classifier': resource})

    @log_helpers.log_method_call
    def delete_flow_classifier(self, context):
        entity_path = 'flow_classifiers/' + context.current['id']
        onos_utils.send_msg(self.onos_path, self.onos_auth, 'delete',
                            entity_path)
