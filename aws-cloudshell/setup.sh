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




#echo "Creates cassandra Directory if it doesn't exists"
```mkdir -p ~/.cassandra```

#echo "Downloading & installing pip2 for python2 in home directory"
```curl -L https://bootstrap.pypa.io/pip/2.7/get-pip.py -o ~/.cassandra/get-pip.py
python2 ~/.cassandra/get-pip.py —user```



To install the cqlsh-expansion python package you can run the following pip2 command.
The command below executes a “pip2 install” that will install the cqlsh-expansion scripts. 
It will also install a requirements file containing a list of dependencies. 
The --user flag tells pip to use the Python user install directory for your platform. 

Typically ~/.local/ on unix based systems.
```pip2 install —user cqlsh-expansion```



#Setup cqlsh-expansion to connect to Amazon Keyspaces


#To use the cqlsh-expansion with Amazon Keyspaces you can use the following post install script or by following the instructions found in the official Amazon Keyspaces documentation.

By default the cqlsh-expansion is not configured with ssl enabled, but the package includes a post install script helper to quickly setup your environment after installation. 
The script will place the necessary configuration and SSL certificate in the user’s .cassandra directory. Amazon Keyspaces only accepts secure connections using Transport Layer Security (TLS). 
Encryption in transit provides an additional layer of data protection by encrypting your data as it travels to and from Amazon Keyspaces. The post install script first will create the .cassandra directory if it does not exist already. 
Then it will copy a preconfigure a cqlshrc file and the Starfield digital certificate into the .cassandra directory. The .cassandra directory will be created in the user home directory as it is the default location. As best practice, please review the post install script before executing. Modifications made by this post install script will not be undone if uninstalling the cqlsh-expansion with pip.

```cqlsh-expansion.init```



#echo "Cleaning up pip2 cache & remove unnecessary files"

```pip2 cache purge
rm -f ~/.cassandra/get-pip.py
pip2 uninstall cqlsh-expansion```
