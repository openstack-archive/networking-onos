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


class ONOSFloatingIP(object):

    """Implementation of ONOS L3 Floating IP Service.

    This class sends Neutron's L3 Floating IP messages to ONOS.
    """
    def send_floatingip_msg(self, msg_type, entity_path, entity):
        onos_utils.send_msg(self.onos_path, self.onos_auth,
                            msg_type, entity_path, entity)

    def handle_create_floatingip(self, fip_dict):
        self.send_floatingip_msg('post', 'floatingips',
                                 {'floatingip': fip_dict})

    def handle_update_floatingip(self, id, fip_dict):
        url_path = 'floatingips' + '/' + id
        self.send_floatingip_msg('put', url_path,
                                 {'floatingip': fip_dict})

    def handle_delete_floatingip(self, id):
        url_path = 'floatingips' + '/' + id
        self.send_floatingip_msg('delete', url_path, None)
