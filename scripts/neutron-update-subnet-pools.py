#!/usr/bin/env python
#
# http://samos-it.com/posts/neutron-multiple-allocation-pools-single-subnet.html
#
# This script allows to add several allocation pools to one subnet
# For authentication it uses environment variables. Before running this script you need to source your openrc
#
# source openrc
#
# Usage example:
# neutron-update-subnet-pools.py --subnet a0620e1c-a4b6-48b8-b2a0-79bc7a2ec509 --payload "{subnet: {allocation_pools: [{start: 10.2.1.3, end: 10.2.1.15}, {start: 10.2.1.17, end: 10.2.1.17}, {start: 10.2.1.19, end: 10.2.1.254}]}}"

import os
# import logging
import argparse
import yaml
from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--subnet", metavar="subnet", required=True, help="Subnet UUID")
parser.add_argument("--payload", metavar="payload", required=True, help="Payload in JSON format. In short it is a list of subnet pools. \
Example: {subnet: {allocation_pools: [{start: 10.0.2.3, end: 10.0.2.15}, {start: 10.0.2.17, end: 10.0.2.17}, {start: 10.0.2.19, end: 10.0.2.254}]}}")
args = parser.parse_args()

# logging.basicConfig(level=logging.DEBUG)
auth_url=os.environ['OS_AUTH_URL']
username=os.environ['OS_USERNAME']
password=os.environ['OS_PASSWORD']
project_name=os.environ.get('OS_PROJECT_NAME')
tenant_name=os.environ.get('OS_TENANT_NAME')
project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default')
project_domain_id=os.environ.get('OS_PROJECT_DOMAIN_ID', 'default')
user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default')
user_domain_id=os.environ.get('OS_USER_DOMAIN_ID', 'default')
identity_api_version=os.environ.get('OS_IDENTITY_API_VERSION', '2')

if identity_api_version == '3':
    auth = identity.Password(auth_url=auth_url,
                             username=username,
                             password=password,
                             project_name=project_name,
                             project_domain_id=project_domain_id,
                             project_domain_name=project_domain_name,
                             user_domain_id=user_domain_id,
                             user_domain_name=user_domain_name)

else:
    auth = identity.Password(auth_url=auth_url,
                             username=username,
                             password=password,
                             tenant_name=tenant_name)

sess = session.Session(auth=auth)
neutron = client.Client(session=sess)

print("\nCurrent configuration of the subnet "+args.subnet+"\n")
print(neutron.show_subnet(args.subnet))
print("\nUpdating subnet "+args.subnet+"\n")

neutron.update_subnet(args.subnet, yaml.load(args.payload))

print("\nNew configuration of the subnet "+args.subnet+"\n")
print(neutron.show_subnet(args.subnet))
