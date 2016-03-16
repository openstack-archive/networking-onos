#!/bin/bash
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

# this script creates rpm package for networking-onos

set -e

# move to networking-onos directory
pushd ../../

# store the path for plugin directory
PLUGIN_DIR="$(pwd)"

# create rpm build environment
rm -rf ~/rpmbuild
mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}

# Get the version from PKG-INFO
VERSION=`cat PKG-INFO | grep Version | grep -o '[0-9]*[.][0-9]*[.][0-9]*'`

# Create the tarball and untar it
python setup.py sdist --dist-dir ~/rpmbuild/SOURCES

# Copy the rpm spec file into rpm specs directory
cp ${PLUGIN_DIR}/package/rpm/networking-onos.spec ~/rpmbuild/SPECS

# update version in spec file
sed -ie "s/Version:\s\+XXX/Version:        ${VERSION}/" ~/rpmbuild/SPECS/networking-onos.spec

# Build the package
rpmbuild -bs ~/rpmbuild/SPECS/networking-onos.spec

# copy the rpm package to respective directory
cp ~/rpmbuild/SRPMS/*.rpm $PLUGIN_DIR/package/rpm/
