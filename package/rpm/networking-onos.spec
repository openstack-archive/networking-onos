Name:      networking-onos
Version:   XXX
Release:   1.0
Summary:   ONOS driver for OpenStack connectivity

Group:     Applications/System
License:   ASL 2.0
URL:       https://pypi.python.org/pypi/%{name}
Source:    %{name}-%{version}.tar.gz

BuildArch: noarch
BuildRoot: ~/rpmbuild

%description
This package provides onos networking driver for OpenStack Neutron
    - Neutron ML2 & L3 plugin functionality
    - Service function chaining using networking-sfc
    - Traffic classification using networking-sfc's flow classifier extension.

%prep
%setup -q

%clean
rm -rf %{buildroot}
