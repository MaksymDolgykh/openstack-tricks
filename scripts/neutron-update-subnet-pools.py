#!/usr/bin/env python

# http://samos-it.com/posts/neutron-multiple-allocation-pools-single-subnet.html
#
# This script allows to add several allocation pools to subnet
# For authentication it uses environment variable. Before running this script you need to source your openrc
# source openrc
# example
# neutron-update-subnet-pools.py --subnet 588ac3f7-7f57-4e2e-8c23-ba29e33fa114 --payload "{subnet: {allocation_pools: [{start: 10.0.2.3, end: 10.0.2.15}, {start: 10.0.2.17, end: 10.0.2.17}, {start: 10.0.2.19, end: 10.0.2.254}]}}"

import os
# import logging
import argparse
import yaml
from neutronclient.neutron import client


parser = argparse.ArgumentParser()
parser.add_argument("--subnet", metavar="subnet", required=True, help="Subnet UUID")
parser.add_argument("--payload", metavar="payload", required=True, help="Payload in JSON format. In short it is a list of subnet pools. \
Example: {subnet: {allocation_pools: [{start: 10.0.2.3, end: 10.0.2.15}, {start: 10.0.2.17, end: 10.0.2.17}, {start: 10.0.2.19, end: 10.0.2.254}]}}")
args = parser.parse_args()

auth_url = os.environ['OS_AUTH_URL']

# logging.basicConfig(level=logging.INFO)
neutron = client.Client('2.0', username=os.environ['OS_USERNAME'], password=os.environ['OS_PASSWORD'], tenant_name=os.environ['OS_TENANT_NAME'], auth_url=auth_url)


print("\nCurrent configuration os the subnet\n")
print(neutron.show_subnet(args.subnet))
print("\nUpdating subnet\n")
neutron.update_subnet(args.subnet, yaml.load(args.payload))
print("\nNew configuration os the subnet\n")
print(neutron.show_subnet(args.subnet))
