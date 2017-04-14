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
from neutron.callbacks import events
from neutron.callbacks import registry
from neutron.callbacks import resources

from networking_onos.extensions import constant as onos_const


_OPERATION_MAPPING = {
    events.PRECOMMIT_CREATE: onos_const.ONOS_CREATE,
    events.PRECOMMIT_UPDATE: onos_const.ONOS_UPDATE,
    events.PRECOMMIT_DELETE: onos_const.ONOS_DELETE,
    events.AFTER_CREATE: onos_const.ONOS_CREATE,
    events.AFTER_UPDATE: onos_const.ONOS_UPDATE,
    events.AFTER_DELETE: onos_const.ONOS_DELETE,
}

_RESOURCE_MAPPING = {
    resources.SECURITY_GROUP: onos_const.ONOS_SG,
    resources.SECURITY_GROUP_RULE: onos_const.ONOS_SG_RULE,
}


class OnosSecurityGroupHandler(object):

    def __init__(self, precommit, postcommit):
        assert postcommit is not None
        self._precommit = precommit
        self._postcommit = postcommit
        self._subscribe()

    def _subscribe(self):
        if self._precommit is not None:
            for event in (events.PRECOMMIT_CREATE, events.PRECOMMIT_DELETE):
                registry.subscribe(self.sg_callback_precommit,
                                   resources.SECURITY_GROUP, event)
                registry.subscribe(self.sg_callback_precommit,
                                   resources.SECURITY_GROUP_RULE, event)

            registry.subscribe(self.sg_callback_precommit,
                               resources.SECURITY_GROUP,
                               events.PRECOMMIT_UPDATE)

        for event in (events.AFTER_CREATE, events.AFTER_DELETE):
            registry.subscribe(self.sg_callback_postcommit,
                               resources.SECURITY_GROUP, event)
            registry.subscribe(self.sg_callback_postcommit,
                               resources.SECURITY_GROUP_RULE, event)

        registry.subscribe(self.sg_callback_postcommit,
                           resources.SECURITY_GROUP, events.AFTER_UPDATE)

    def _sg_callback(self, callback, resource, event, trigger, **kwargs):
        context = kwargs['context']
        res = kwargs.get(resource)
        res_id = kwargs.get("%s_id" % resource)
        if res_id is None:
            res_id = res.get('id')
        ops = _OPERATION_MAPPING[event]
        res_type = _RESOURCE_MAPPING[resource]
        res_dict = res

        callback(context, ops, res_type, res_id, res_dict)

    def sg_callback_precommit(self, resource, event, trigger, **kwargs):
        self._sg_callback(self._precommit, resource, event, trigger, **kwargs)

    def sg_callback_postcommit(self, resource, event, trigger, **kwargs):
        self._sg_callback(self._postcommit, resource, event, trigger, **kwargs)
