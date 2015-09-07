# Copyright (c) 2015 Huawei Technologies India Pvt Ltd
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

from oslo_log import log as logging
from oslo_serialization import jsonutils
import requests


LOG = logging.getLogger(__name__)


def send_msg(onos_path, onos_auth, msg_type, entity_path, entity=None):
    """Send message to the ONOS controller."""

    path = '/'.join([onos_path, entity_path])
    hdr = {'Content-Type': 'application/json'}
    body = jsonutils.dumps(entity, indent=2) if entity else None
    LOG.debug("Sending MSG_TYPE (%(msg)s) URL (%(path)s) "
              "OBJECT (%(entity)s) BODY (%(body)s)",
              {'msg': msg_type, 'path': path,
               'entity': entity, 'body': body})
    req = requests.request(method=msg_type, url=path,
                           headers=hdr, data=body,
                           auth=onos_auth)
    # Let's raise voice for an error
    req.raise_for_status()


def safe_delete_from_dict(dict, keys):
    """Ignore key errors when deleting from a dictionary."""
    for key in keys:
        dict.pop(key, None)
