#!/bin/bash
#--------------------------------------------------------------------
#Description: connect to Amazon Keyspaces or Apache Cassandra using cqlsh using Generated service credentials stored in secrets manager
#author: Michael Raney
#date: 5/11/2020
#--------------------------------------------------------------------

#dependency on jq (JSON parsing utility)
#### https://stedolan.github.io/jq/download/
#### Debian/Ubuntu   apt-get install jq
#### OS X home brew  brew install jq

#paramters
#$1 secret-id
#$2 CQL statement

mysecret=$(aws secretsmanager get-secret-value --secret-id "$1" --region "$2" --query SecretString --output text)

username=$(jq --raw-output '.username' <<< $mysecret)
password=$(jq --raw-output '.password' <<< $mysecret)
host=$(jq --raw-output '.host' <<< $mysecret)
port=$(jq --raw-output '.port' <<< $mysecret)

echo "executing.. cqlsh" $host $port "-u *** -p *** ${@:3}"
cqlsh-expansion $host $port -u $username -p $password "${@:3}"
