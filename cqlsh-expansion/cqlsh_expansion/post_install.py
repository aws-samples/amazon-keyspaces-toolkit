#!/usr/cqlsh_expansion/env python
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Initialize_cassandra_directory function checks if .cassandra directory exists in user's home path,
## if not it creates the directory and copies cqlshrc and sf-class2-root.crt files if files already exists
### If so function will not move those files

import getpass
import os
import shutil
import site



def initialize_cassandra_directory():

    user_dir = os.path.expanduser('~')
    config_dir = os.path.join(user_dir, '.cassandra')
    cert_dest_file = os.path.join(config_dir, 'sf-class2-root.crt')
    cqlshrc_dest_file = os.path.join(config_dir, 'cqlshrc')

    print('Initializing .cassandra directory with SSL cert and cqlshrc file in user directory')

    try:

        if not os.path.exists(config_dir):
            print('Creating .cassandra directory in home path ' + user_dir)
            os.mkdir(config_dir)
        else:
            print('Directory already exists ' + config_dir)

        cert_found = False

        for one_path in site.getusersitepackages():
            cert_install_file = os.path.join(one_path, 'cqlsh_expansion', 'sf-class2-root.crt')
            if os.path.exists(cert_install_file):
                print('Copying cert from ' + cert_install_file + ' to ' + cert_dest_file)
                shutil.copy(cert_install_file, cert_dest_file)
                cert_found = True
                break

        if not cert_found:
            for one_path in site.getsitepackages():
                cert_install_file = os.path.join(one_path, 'cqlsh_expansion', 'sf-class2-root.crt')
                if os.path.exists(cert_install_file):
                    print('Copying cert from ' + cert_install_file + ' to ' + cert_dest_file)
                    shutil.copy(cert_install_file, cert_dest_file)
                    cert_found = True
                    break

        if not cert_found:
            print('sf-class2-root.crt not found ')

        cqlshrc_found = False
        for one_path in site.getusersitepackages():
            cqlshrc_install_file = os.path.join(one_path, 'cqlsh_expansion', 'cqlshrc_template')
            if os.path.exists(cqlshrc_install_file):
                print('Copying cqlshrc from ' + cqlshrc_install_file + ' to ' + cqlshrc_dest_file)
                shutil.copy(cqlshrc_install_file, cqlshrc_dest_file)
                cqlshrc_found = True
                break

        if not cqlshrc_found:
            for one_path in site.getsitepackages():
                cqlshrc_install_file = os.path.join(one_path, 'cqlsh_expansion', 'cqlshrc_template')
                if os.path.exists(cqlshrc_install_file):
                    print('Copying cqlshrc from '+ cqlshrc_install_file + ' to ' + cqlshrc_dest_file)
                    shutil.copy(cqlshrc_install_file, cqlshrc_dest_file)
                    cqlshrc_found = True
                    break

        if not cqlshrc_found:
            print('cqlshrc_template not found ')

        print('Post installation configuration for expansion utility completed')

    except BaseException as error:
        print('Oops! an exception occurred: {}'.format(error))


if __name__ == '__main__':
    initialize_cassandra_directory()
