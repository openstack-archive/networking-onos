#!/usr/bin/env bash

set -xe

# Drop a token that marks the build as coming from openstack infra
GATE_DEST=$BASE/new
DEVSTACK_PATH=$GATE_DEST/devstack

cat <<EOF >> $DEVSTACK_PATH/localrc
PROJECTS="onos_git_repo $PROJECTS"
IS_GATE=True

# Switch to using the ONOS's L3 implementation
ONOS_L3=False

# Enable debug logs for onos ovsdb
ONOS_VTN_DEBUG_LOGS=True

EOF
