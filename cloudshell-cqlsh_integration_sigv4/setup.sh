#!/bin/sh
echo " Download the Starfield digital certificate to connect using SSL/TLS"
curl https://certs.secureserver.net/repository/sf-class2-root.crt --output  ~/keyspaces.crt
export PATH=$PATH:amazon-keyspaces-toolkit/cqlsh-expansion/bin
sudo yum install -y python2-pip
sudo pip2 install -y cassandra-sigv4
cp ~/amazon-keyspaces-toolkit/cloudshell-cqlsh_integration_sigv4/cqlshrc ~/.cassandra/cqlshrc