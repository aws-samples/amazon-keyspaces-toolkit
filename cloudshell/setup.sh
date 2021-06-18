#!/bin/sh

# echo "Setting up python2 as default python"
# echo "alias python='/usr/bin/python2'" >>  ~/.bashrc
# source ~/.bashrc
echo " Creating cassandra Dir"
mkdir ~/.cassandra
echo " Downloading & installing pip2 for python2 in home directory"
curl -L https://bootstrap.pypa.io/pip/2.7/get-pip.py  -o ~/.cassandra/get-pip.py
python2 ~/.cassandra/get-pip.py --user
echo "Installing cassandra-sigv4 using pip2 in home directory"
pip2 install --user cassandra-sigv4
pip2 install --user cqlsh
echo "downloading cqlsh-expansion files & moving them to local user bin directory"
wget https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlsh-expansion/bin/cqlsh-expansion -P /home/cloudshell-user/.local/bin
wget https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlsh-expansion/bin/cqlsh-expansion.py -P /home/cloudshell-user/.local/bin

echo "Copying cqlshrc for cassandra user"
wget  https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/cqlshrc -P ~/.cassandra

echo " Download the Starfield digital certificate to connect using SSL/TLS"
curl https://certs.secureserver.net/repository/sf-class2-root.crt --output  ~/.cassandra/keyspaces.crt

sed -i 's;certfile = .*$;certfile = ~/.cassandra/keyspaces.crt;g' ~/.cassandra/cqlshrc