#!/usr/bin/env python

# Copyright 2022 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example of configuring access with security keys for OS Login.

Security keys used for 2-Step Verification have an associated public and
private key pair. This example retrieves the SSH private keys from registered
security keys in the user's Google account. Once retrieved, write the private
keys to files in the .ssh directory, then print an SSH command.

Note: the private key is not secret, and cannot be used without physical access
to the security key device.
"""

import argparse
import os

import googleapiclient.discovery


def write_ssh_key_files(security_keys, directory):
  """Store the SSH key files."""
  key_files = []
  for index, key in enumerate(security_keys):
    key_file = os.path.join(directory, 'google_sk_%s' % index)
    with open(key_file, 'w') as f:
      f.write(key.get('privateKey'))
      os.chmod(key_file, 0o600)
      key_files.append(key_file)
  return key_files


def ssh_command(key_files, username, ip_address):
  """Print the SSH command to connect to an IP address with security keys."""
  parameters = ' '.join(['-i ' + f for f in key_files])
  print('ssh {parameters} {username}@{ip_address}'.format(
      parameters=parameters, username=username, ip_address=ip_address))


def main(user_key, ip_address, directory=None):
  """Configure SSH key files and print SSH command."""
  directory = directory or os.path.join(os.path.expanduser('~'), '.ssh')

  # Create the OS Login API object.
  oslogin = googleapiclient.discovery.build('oslogin', 'v1beta')

  # Retrieve security keys and OS Login username from a user's Google account.
  profile = oslogin.users().getLoginProfile(
      name='users/{}'.format(user_key), view='SECURITY_KEY').execute()
  security_keys = profile.get('securityKeys')
  username = profile.get('posixAccounts')[0].get('username')

  # Write the SSH private key files.
  key_files = write_ssh_key_files(security_keys, directory)

  # Print the SSH command.
  ssh_command(key_files, username, ip_address)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--user_key',
      help='Your primary email address, alias email address, or unique user ID')
  parser.add_argument(
      '--ip_address',
      help='The external IP address of the VM you want to connect to.')
  parser.add_argument(
      '--directory',
      help='The directory to store SSH private keys.')
  args = parser.parse_args()

  main(args.user_key, args.ip_address, args.directory)
