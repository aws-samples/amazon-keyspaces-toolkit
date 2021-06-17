#!/bin/sh
echo " Download the Starfield digital certificate to connect using SSL/TLS"
curl https://certs.secureserver.net/repository/sf-class2-root.crt --output  ~/keyspaces.crt
echo "Setting up python2 as default python"
echo "alias python='/usr/bin/python2'" >>  ~/.bashrc
source ~/.bashrc
echo " Downloading & installing pip2 for python in home directory"
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py -P ~/get-pip.py
python ~/get-pip.py --user
echo "Installing cassandra-sigv4 using pip2 in home directory"
pip2 install --user cassandra-sigv4
echo "Setting up path for cqlsh-expansion"
export PATH=$PATH:~/amazon-keyspaces-toolkit/cloudshell-cqlsh_integration_sigv4/bin
echo "Copying cqlshrc for cassandra user"
cp ~/amazon-keyspaces-toolkit/cloudshell-cqlsh_integration_sigv4/cqlshrc ~/.cassandra/cqlshrc