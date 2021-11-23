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

curl -L https://bootstrap.pypa.io/pip/2.7/get-pip.py -o ~/.cassandra/get-pip.py
python2 ~/.cassandra/get-pip.py —user



# To install the cqlsh-expansion python package executing the following pip2 command. 

echo “Installing cqlsh-expansion "
pip2 install —user cqlsh-expansion


# To configure cqlsh-expanson 

echo “configuring cqlsh-expansion to connect to Amazon Keyspaces”
cqlsh-expansion.init



echo "Cleaning up pip2 cache & remove unnecessary files"

pip2 cache purge
rm -f ~/.cassandra/get-pip.py
pip2 uninstall cqlsh-expansion
