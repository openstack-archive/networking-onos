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

from oslo_config import cfg

from neutron.api.rpc.agentnotifiers import l3_rpc_agent_api
from neutron.api.rpc.handlers import l3_rpc
from neutron.common import constants as q_const
from neutron.common import rpc as n_rpc
from neutron.common import topics
from neutron.db import db_base_plugin_v2
from neutron.db import extraroute_db
from neutron.db import l3_agentschedulers_db
from neutron.db import l3_gwmode_db
from neutron.plugins.common import constants

from networking_onos.common import config   # noqa
from networking_onos.plugins.l3 import floating_ip as onos_fip
from networking_onos.plugins.l3 import router as onos_router


class ONOSL3Plugin(db_base_plugin_v2.NeutronDbPluginV2,
                   extraroute_db.ExtraRoute_db_mixin,
                   l3_gwmode_db.L3_NAT_db_mixin,
                   l3_agentschedulers_db.L3AgentSchedulerDbMixin,
                   onos_router.ONOSRouter,
                   onos_fip.ONOSFloatingIP):

    """Implementation of the ONOS L3 Router Service Plugin.

    This class implements a L3 service plugin that provides
    router and floatingip resources and manages associated
    request/response.
    """
    supported_extension_aliases = ["router", "ext-gw-mode", "extraroute"]

    def __init__(self):
        self.setup_rpc()
        self.onos_path = cfg.CONF.onos.url_path
        self.onos_auth = (cfg.CONF.onos.username, cfg.CONF.onos.password)

    def setup_rpc(self):
        self.topic = topics.L3PLUGIN
        self.conn = n_rpc.create_connection(new=True)
        self.agent_notifiers.update(
            {q_const.AGENT_TYPE_L3: l3_rpc_agent_api.L3AgentNotifyAPI()})
        self.endpoints = [l3_rpc.L3RpcCallback()]
        self.conn.create_consumer(self.topic, self.endpoints, fanout=False)
        self.conn.consume_in_threads()

    def get_plugin_type(self):
        return constants.L3_ROUTER_NAT

    def get_plugin_description(self):
        """returns plug-in description"""
        return ("L3 Router Service Plug-in for basic L3 forwarding using ONOS")

    def create_router(self, context, router):
        router_dict = super(ONOSL3Plugin, self).create_router(context, router)
        self.handle_create_router(router_dict)
        return router_dict

    def update_router(self, context, id, router):
        router_dict = super(ONOSL3Plugin, self).update_router(context, id,
                                                              router)
        self.handle_update_router(router_dict, id)
        return router_dict

    def delete_router(self, context, id):
        super(ONOSL3Plugin, self).delete_router(context, id)
        self.handle_delete_router(id)

    def create_floatingip(self, context, floatingip,
                          initial_status=q_const.FLOATINGIP_STATUS_ACTIVE):
        fip_dict = super(ONOSL3Plugin, self).create_floatingip(context,
                                                               floatingip,
                                                               initial_status)
        self.handle_create_floatingip(fip_dict)
        return fip_dict

    def update_floatingip(self, context, id, floatingip):
        fip_dict = super(ONOSL3Plugin, self).update_floatingip(context, id,
                                                               floatingip)
        self.handle_update_floatingip(id, fip_dict)
        return fip_dict

    def delete_floatingip(self, context, id):
        super(ONOSL3Plugin, self).delete_floatingip(context, id)
        self.handle_delete_floatingip(id)

    def add_router_interface(self, context, router_id, interface_info):
        router = super(ONOSL3Plugin, self).add_router_interface(context,
                                                                router_id,
                                                                interface_info)
        intf_add_type = self._get_intf_add_type(router, interface_info)
        self.handle_add_router_interface(router, router_id,
                                         interface_info, intf_add_type)
        return router

    def remove_router_interface(self, context, router_id, interface_info):
        router = super(ONOSL3Plugin, self).remove_router_interface(
            context, router_id, interface_info)
        intf_add_type = self._get_intf_add_type(router, interface_info)
        self.handle_remove_router_interface(router, router_id,
                                            interface_info, intf_add_type)
        return router

    def _get_intf_add_type(self, router_info, intf_info):
        add_by_port, add_by_sub = self._validate_interface_info(intf_info)
        if add_by_sub:
            return onos_router.ADD_INTF_BY_SUBNET

        return onos_router.ADD_INTF_BY_PORT
