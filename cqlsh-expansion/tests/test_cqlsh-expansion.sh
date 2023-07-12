#!/cqlsh_expansion/bash

#Simple test for functionality of Keyspaces cqlsh-expansion.

#arguments
HOST=$1
PORT=$2

cqlsh-expansion  $HOST $PORT --ssl --execute 'SHOW VERSION; SHOW VERSION; SHOW HOST;'

cqlsh-expansion  $HOST $PORT --ssl --execute "CREATE KEYSPACE expansion_test WITH REPLICATION = {'class': 'SingleRegionStrategy'};"

# Introducing 60 seconds sleep as the create commands are async
sleep 60

cqlsh-expansion  $HOST $PORT --ssl --execute 'DESCRIBE KEYSPACE expansion_test;'

cqlsh-expansion  $HOST $PORT --ssl --execute "CREATE TABLE expansion_test.backofftest (id text,name text,description text,details map<text,text>,PRIMARY KEY(id, name)) WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

# Introducing 60 seconds sleep as the create commands are async
sleep 60

cqlsh-expansion  $HOST $PORT --ssl --execute "DESCRIBE TABLE expansion_test.backofftest;"

cqlsh-expansion  $HOST $PORT --ssl --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO expansion_test.backofftest(id, name, description, details) VALUES('1', 'abc', 'xyz', {'key1':'value1'});"

cqlsh-expansion  $HOST $PORT --ssl --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO expansion_test.backofftest(id, name, description, details) VALUES('2', 'efg', 'hij', {'key2':'value2'}) IF NOT EXISTS;"

cqlsh-expansion  $HOST $PORT --ssl --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM expansion_test.backofftest;"

cqlsh-expansion  $HOST $PORT --ssl --execute "CONSISTENCY LOCAL_QUORUM; COPY expansion_test.backofftest TO 'data.csv';COPY expansion_test.backofftest FROM 'data.csv';";

#cqlsh-expansion  $HOST $PORT --ssl --auth-provider "SigV4AuthProvider" \
#            --file /source/test.cql

cqlsh-expansion  $HOST $PORT --ssl --execute "DROP KEYSPACE expansion_test;"

echo "Finished cqlsh-expansion tests"