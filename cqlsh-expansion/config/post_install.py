#!/usr/bin/env python
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
    user = getpass.getuser()
    user_dir = os.path.expanduser('~'+user)
    installation_dir = site.USER_SITE + '/' + 'config/'
    config_dir = os.path.join( user_dir, '.cassandra')
    cert_dir = os.path.join(config_dir, 'sf-class2-root.crt')
    cqlshrc_dir = os.path.join(config_dir, 'cqlshrc')

    try:
        if not os.path.exists(config_dir):
            print('Creating .cassandra directory in home path ' + user_dir)
            os.mkdir(config_dir)
        else:
            print('Directory already exists ' + config_dir)

        if not os.path.exists(cert_dir):
            print('Moving sf-class2-root cert file to ' + cert_dir)
            shutil.copy(installation_dir + 'sf-class2-root.crt', config_dir)
        else:
            print('sf-class2-root cert file already exists ' + cert_dir)

        if not os.path.exists(cqlshrc_dir):
            print('Moving cqlshrc config file to ' + cqlshrc_dir)
            shutil.copy(installation_dir + 'cqlshrc_template', cqlshrc_dir)

        else:
            print('cqlshrc config file already exists ' + cqlshrc_dir)

        print('Post installation configuration for expansion utility completed')

    except BaseException as error:
        print('Oops! an exception occurred: {}'.format(error))


