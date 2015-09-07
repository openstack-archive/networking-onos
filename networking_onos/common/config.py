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

from oslo_config import cfg

ONOS_DRIVER_OPTS = [
    cfg.StrOpt('url_path',
               default='',
               help=_('ONOS ReST interface URL')),
    cfg.StrOpt('username',
               default='',
               help=_('Username for authentication.')),
    cfg.StrOpt('password',
               default='',
               secret=True,  # do not expose value in the logs
               help=_('Password for authentication.'))
]

cfg.CONF.register_opts(ONOS_DRIVER_OPTS, "onos")
