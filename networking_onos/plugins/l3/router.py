# Copyright (C) 2015 Huawei Technologies India Pvt Ltd.
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

from networking_onos.common import utils as onos_utils

ADD_INTF_BY_PORT = 1
ADD_INTF_BY_SUBNET = 2


class ONOSRouter(object):

    """Implementation of ONOS L3 Router Service.

    This class sends Neutron's L3 router messages to ONOS.
    """
    def send_router_msg(self, msg_type, entity_path, entity):
        onos_utils.send_msg(self.onos_path, self.onos_auth,
                            msg_type, entity_path, entity)

    def handle_create_router(self, router_dict):
        self.send_router_msg('post', 'routers',
                             {'router': router_dict})

    def handle_update_router(self, router_dict, id):
        url_path = 'routers' + '/' + id
        resource = router_dict.copy()
        onos_utils.safe_delete_from_dict(resource,
                                         ['id', 'tenant_id', 'status'])
        self.send_router_msg('put', url_path, {'router': resource})

    def handle_delete_router(self, id):
        url_path = 'routers' + '/' + id
        self.send_router_msg('delete', url_path, None)

    def handle_add_router_interface(self, new_router, router_id,
                                    interface_info, intf_add_type):
        url_path = 'routers' + '/' + router_id + '/add_router_interface'
        router_dict = self._prepare_router_dict(router_id, interface_info,
                                                new_router, intf_add_type)
        self.send_router_msg('put', url_path, router_dict)

    def handle_remove_router_interface(self, new_router, router_id,
                                       interface_info, intf_add_type):
        url_path = 'routers' + '/' + router_id + '/remove_router_interface'
        router_dict = self._prepare_router_dict(router_id, interface_info,
                                                new_router, intf_add_type)
        self.send_router_msg('put', url_path, router_dict)

    def _prepare_router_dict(self, router_id, interface_info,
                             new_router, add_type):
        if add_type == ADD_INTF_BY_SUBNET:
            _port_id = new_router['port_id']
            _subnet_id = interface_info['subnet_id']
        else:
            _port_id = interface_info['port_id']
            _subnet_id = new_router['subnet_id']

        router_dict = {'subnet_id': _subnet_id,
                       'port_id': _port_id,
                       'id': router_id,
                       'tenant_id': new_router['tenant_id']}
        return router_dict
