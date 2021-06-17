#!/bin/sh
echo " Download the Starfield digital certificate to connect using SSL/TLS"
curl https://certs.secureserver.net/repository/sf-class2-root.crt --output  ~/keyspaces.crt
export PATH=$PATH:amazon-keyspaces-toolkit/cqlsh-expansion/bin
curl -LO https://bootstrap.pypa.io/pip/2.7/get-pip.py
python get-pip.py --user
sudo pip2 install --user cassandra-sigv4
cp ~/amazon-keyspaces-toolkit/cloudshell-cqlsh_integration_sigv4/cqlshrc ~/.cassandra/cqlshrc