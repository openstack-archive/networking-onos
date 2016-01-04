#!/bin/bash
#
# devstack/plugin.sh
# Functions to control the configuration and operation of the onos service

# Save trace setting
XTRACE=$(set +o | grep xtrace)
set +o xtrace

# ONOS directories
NETWORKING_ONOS_DIR=$DEST/networking-onos
ONOS_DIR=$DEST/onos

# Make sure $ONOS_DIR exists
mkdir -p $ONOS_DIR

# Import utility functions
source $TOP_DIR/functions
source $NETWORKING_ONOS_DIR/devstack/functions

# Import bridge data
source $TOP_DIR/lib/neutron_plugins/ovs_base

# Import ONOS settings
source $NETWORKING_ONOS_DIR/devstack/settings.onos
source $NETWORKING_ONOS_DIR/devstack/onos-releases/$ONOS_RELEASE

# Utilities functions for setting up Java
source $NETWORKING_ONOS_DIR/devstack/setup_java.sh

# Import Entry Points
# -------------------
source $NETWORKING_ONOS_DIR/devstack/entry_points


if [[ "$ONOS_USING_EXISTING_JAVA" == "True" ]]
then
    echo 'Using installed java.'
    java -version || exit 1
fi

# main loop
if is_service_enabled onos-server; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        setup_onos_package
        install_onos
        configure_onos
        init_onos
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        configure_neutron_onos
        # This has to start before Neutron
        start_onos
    elif [[ "$1" == "stack" && "$2" == "post-extra" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_onos
        cleanup_onos
    fi

    if [[ "$1" == "clean" ]]; then
        # no-op
        :
    fi
fi

if is_service_enabled onos-compute; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        install_onos_compute
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        if is_service_enabled nova; then
            create_nova_conf_neutron
        fi
        bind_onos_controller
        # ONOS vtn will create $OVS_BR
        wait_for_active_bridge $OVS_BR $ONOS_RETRY_SLEEP_INTERVAL $ONOS_BOOT_WAIT
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # no-op
        :
    elif [[ "$1" == "stack" && "$2" == "post-extra" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        cleanup_onos_compute
    fi

    if [[ "$1" == "clean" ]]; then
        # no-op
        :
    fi
fi

if is_service_enabled onos-neutron; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        install_onos_neutron_thin_ml2_driver
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        configure_neutron_onos
    elif [[ "$1" == "stack" && "$2" == "post-extra" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack" ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "clean" ]]; then
        # no-op
        :
    fi
fi

# Restore xtrace
$XTRACE
