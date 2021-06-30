#!/bin/sh
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

echo "Creates cassandra Directory if it doesn't exists"
mkdir -p ~/.cassandra

echo "Downloading & installing pip2 for python2 in home directory"
curl -L https://bootstrap.pypa.io/pip/2.7/get-pip.py  -o ~/.cassandra/get-pip.py
python2 ~/.cassandra/get-pip.py --user

echo "Installing cqlsh & cassandra-sigv4 using pip2 in home directory"
pip2 install --user cassandra-sigv4
pip2 install --user cqlsh

echo "downloading cqlsh-expansion files & moving them to local user bin directory"
wget https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlsh-expansion/bin/cqlsh-expansion -P /home/cloudshell-user/.local/bin
chmod +x /home/cloudshell-user/.local/bin/cqlsh-expansion
wget https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlsh-expansion/bin/cqlsh-expansion.py -P /home/cloudshell-user/.local/bin

echo "Copying cqlshrc for cassandra user"
wget  https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlshrc -P ~/.cassandra

echo "Download the Starfield digital certificate to connect using SSL/TLS"
curl https://certs.secureserver.net/repository/sf-class2-root.crt --output  ~/.cassandra/keyspaces.crt
sed -i 's;certfile = .*$;certfile = ~/.cassandra/keyspaces.crt;g' ~/.cassandra/cqlshrc

echo "Cleaning up pip2 cache & remove unneccesary files"
pip2 cache purge
rm -f ~/.cassandra/get-pip.py