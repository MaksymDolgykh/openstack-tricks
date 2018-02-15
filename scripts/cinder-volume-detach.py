#!/usr/bin/env python
#
# In my experience I had a situation when cinder volume is attached to the nova instance
# which doesn't exist any more. It is not possible neither to detach nor to delete such volume with CLI.
# This might happen due to one of the bugs
# https://bugs.launchpad.net/nova/+bug/1463856
# https://bugs.launchpad.net/nova/+bug/1335889
#
# However it is possible to detach (then delete, if required) it with direct API call.
# Another way to resolve this problem is to edit cinder database directly. But I think it is better to avoid
# the direct editing of the database.
#
# The scope of this script is to help to resolve such situation.
#
# For the authentication it uses environment variables.
# Before running this script you need to source your openrc
#
# source openrc
#
# Usage example:
#
# cinder-volume-detach.py --volume_id 18e58cdf-b7be-4ce7-a1a4-d3b3017a5509
#

import os
import time
# import logging
import argparse
from keystoneauth1 import identity
from keystoneauth1 import session
from cinderclient import client
import pprint


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--volume_id", metavar="volume_id", required=True, help="Volume UUID")
args = parser.parse_args()

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
volume_api_version=os.environ.get('OS_VOLUME_API_VERSION', '2')

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
cinder = client.Client(volume_api_version, session=sess)

volume = cinder.volumes.get(args.volume_id)
print('\nCurrent attachments of the volume '+args.volume_id+':\n')
pprint.pprint(volume._info['attachments'])
print('Status: '),
pprint.pprint(volume._info['status'])

print('\nDetaching volume '+args.volume_id+'\n')
volume.detach()

while volume._info['status'] in  ['detaching', 'in-use']:
    print('.'),
    volume = cinder.volumes.get(args.volume_id)
    time.sleep(1)

print('\nCurrent attachments of the volume '+args.volume_id+':\n')
pprint.pprint(volume._info['attachments'])
print('Status: '),
pprint.pprint(volume._info['status'])
