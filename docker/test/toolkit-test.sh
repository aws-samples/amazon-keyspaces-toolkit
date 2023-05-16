#!/bin/bash

#Simple test for functionality of Keyspaces toolkit.

#arguments
SERVICEUSERNAME=$1
SERVICEPASSWORD=$2
SECRETKEY=$3
HOST=$4
PORT=$5

# default aws region for secretsmanager
DEFAULT_REGION=us-east-1

echo $SECRETKEY
echo $HOST
echo $PORT
echo $DEFAULT_REGION

#example run from the root of the project
#docker/test/toolkit-test.sh testuser+1-at-963740746376 gUuus3wDFt9Oli6mLeY7G+arlGdlL/ExampleKey= examplesecret4 cassandra.us-east-1.amazonaws.com 9142

docker build --tag amazon/amazon-keyspaces-toolkit -f Dockerfile . --build-arg CLI_VERSION=2.1.27

docker run --rm -t --entrypoint cqlsh amazon/amazon-keyspaces-toolkit --version

docker run --rm -t \
        -v "$(pwd)":/source \
        --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
        $HOST $PORT \
        -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" --ssl \
        --execute "SHOW VERSION; SHOW HOST;"

docker run --rm -t \
    -v "$(pwd)":/source \
    --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
    $HOST $PORT \
    -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" --ssl \
    --execute "CREATE KEYSPACE toolkit_test WITH
    REPLICATION = {'class': 'SingleRegionStrategy'};"

docker run --rm -t \
              -v "$(pwd)":/source \
              --entrypoint aws-cqlsh-expansion-expo-backoff.sh amazon/amazon-keyspaces-toolkit \
              30 120 \
              $HOST $PORT \
              --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
              --execute "DESCRIBE KEYSPACE toolkit_test;"

docker run --rm -t \
        -v "$(pwd)":/source \
        --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
        $HOST $PORT \
        -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" --ssl \
        --execute "CREATE TABLE toolkit_test.backofftest(
         id text,
         name text,
         description text,
         details map<text,text>,
         PRIMARY KEY(id, name))
         WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

docker run --rm -t \
          -v "$(pwd)":/source \
          --entrypoint aws-cqlsh-expansion-expo-backoff.sh amazon/amazon-keyspaces-toolkit \
          30 360 \
          $HOST $PORT \
          --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
          --execute "DESCRIBE TABLE toolkit_test.backofftest;"

docker run --rm -t \
          -v "$(pwd)":/source \
          --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
          $HOST $PORT \
          --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
          --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO toolkit_test.backofftest(id, name, description, details) VALUES('1', 'abc', 'xyz', {'key1':'value1'});"

docker run --rm -t \
                    -v "$(pwd)":/source \
                    --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
                    $HOST $PORT \
                    --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
                    --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO toolkit_test.backofftest(id, name, description, details) VALUES('2', 'efg', 'hij', {'key2':'value2'}) IF NOT EXISTS;"

docker run --rm -t \
            -v "$(pwd)":/source \
            --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
            $HOST $PORT \
            --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
            --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM toolkit_test.backofftest;"

docker run --rm -t \
                -v "$(pwd)":/source \
                --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
                $HOST $PORT \
                --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
                --execute "CONSISTENCY LOCAL_QUORUM; COPY toolkit_test.backofftest TO 'data.csv';COPY toolkit_test.backofftest FROM 'data.csv';";

docker run --rm -t   \
                -v "$(pwd)":/source \
                --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
                $HOST $PORT \
                --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --cqlshrc="/source/docker/test/default_cqlshrc" \
                --file /source/docker/test/test.cql

docker run --rm -t \
              -v "$(pwd)":/source \
              --entrypoint cqlsh amazon/amazon-keyspaces-toolkit \
              $HOST $PORT \
              -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
              --execute "DROP KEYSPACE toolkit_test;"

echo "Finished cqlsh tests"
#secrets manager helper
echo "secrets manager helper tests"

docker run --rm -t \
    -v "$(pwd)":/source \
    -v ~/.aws:/root/.aws \
    --entrypoint aws \
     amazon/amazon-keyspaces-toolkit \
     secretsmanager create-secret --name $SECRETKEY --region $DEFAULT_REGION \
    --description "Store Amazon Keyspaces Generated Service Credentials" \
    --secret-string "{\"username\":\"$SERVICEUSERNAME\", \"password\":\"$SERVICEPASSWORD\", \"host\":\"$HOST\", \"port\":\"$PORT\"}"

docker run --rm -t \
   -v "$(pwd)":/source \
   -v ~/.aws:/root/.aws \
   --entrypoint aws-sm-cqlsh.sh \
   amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
    --execute "SHOW VERSION; SHOW HOST;"

docker run --rm -t \
    -v "$(pwd)":/source \
    -v ~/.aws:/root/.aws \
    --entrypoint aws-sm-cqlsh.sh \
     amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
    --execute "CREATE KEYSPACE sm_toolkit_test WITH REPLICATION = {'class': 'SingleRegionStrategy'};"

 docker run --rm -t \
    -v "$(pwd)":/source \
    -v ~/.aws:/root/.aws \
    --entrypoint aws-sm-cqlsh-expo-backoff.sh \
    amazon/amazon-keyspaces-toolkit $SECRETKEY 30 120 $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
     --execute "DESCRIBE KEYSPACE sm_toolkit_test;"

 docker run --rm -t \
         -v "$(pwd)":/source \
         -v ~/.aws:/root/.aws \
         --entrypoint aws-sm-cqlsh.sh \
          amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
          --execute "CREATE TABLE sm_toolkit_test.backofftest (
           id text,
           name text,
           description text,
           details map<text,text>,
           PRIMARY KEY(id, name))
           WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

docker run --rm -t \
           -v "$(pwd)":/source \
           -v ~/.aws:/root/.aws \
           --entrypoint aws-sm-cqlsh-expo-backoff.sh \
           amazon/amazon-keyspaces-toolkit $SECRETKEY 30 120 $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
             --execute "DESCRIBE TABLE sm_toolkit_test.backofftest;"

docker run --rm -t \
            -v "$(pwd)":/source \
            -v ~/.aws:/root/.aws \
            --entrypoint aws-sm-cqlsh.sh \
            amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
           --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO sm_toolkit_test.backofftest(id, name, description, details) VALUES('1', 'abc', 'xyz',{'key1':'value1'});"

docker run --rm -t  \
           -v "$(pwd)":/source \
           -v ~/.aws:/root/.aws \
           --entrypoint  aws-sm-cqlsh.sh \
           amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
          --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO sm_toolkit_test.backofftest(id, name, description, details) VALUES('2', 'efg', 'hij',{'key2':'value2'}) IF NOT EXISTS;"

docker run --rm -t  \
           -v "$(pwd)":/source \
           -v ~/.aws:/root/.aws \
           --entrypoint aws-sm-cqlsh.sh \
           amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
            --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM sm_toolkit_test.backofftest;"

docker run --rm -t  \
             -v "$(pwd)":/source \
             -v ~/.aws:/root/.aws \
             --entrypoint  aws-sm-cqlsh.sh \
             amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
            --execute "CONSISTENCY LOCAL_QUORUM; COPY sm_toolkit_test.backofftest TO 'data.csv';COPY sm_toolkit_test.backofftest FROM 'data.csv';";

docker run --rm -t  \
           -v "$(pwd)":/source \
           -v ~/.aws:/root/.aws \
           --entrypoint  aws-sm-cqlsh.sh \
           amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
          --file /source/docker/test/test.cql

docker run --rm -t \
-v "$(pwd)":/source \
-v ~/.aws:/root/.aws \
--entrypoint aws-sm-cqlsh.sh \
 amazon/amazon-keyspaces-toolkit $SECRETKEY $DEFAULT_REGION $HOST $PORT  --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
 --execute "DROP KEYSPACE sm_toolkit_test;"

echo "Finished sm helper tests"

#cqlsh-expansion test
echo "cqlsh-expansion tests with auth provider SigV4AuthProvider"

docker run --rm -t \
   -v ~/.aws:/root/.aws \
   amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
   --execute "SHOW VERSION; SHOW HOST;"

#connect without sigv4
docker run --rm -t \
           -v "$(pwd)":/source \
           amazon/amazon-keyspaces-toolkit $HOST $PORT \
           -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl --cqlshrc="/source/docker/test/default_cqlshrc" \
           --execute "SHOW VERSION; SHOW HOST;"

# cqlsh-expansion tests with auth provider SigV4AuthProvider from cqlshrc file
docker run --rm -t \
    -v ~/.aws:/root/.aws \
    amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
    --execute "CREATE KEYSPACE expansion_toolkit_test WITH REPLICATION = {'class': 'SingleRegionStrategy'};"

 docker run --rm -t \
    -v ~/.aws:/root/.aws \
    --entrypoint aws-cqlsh-expansion-expo-backoff.sh \
    amazon/amazon-keyspaces-toolkit  30 120 $HOST $PORT --ssl \
     --execute "DESCRIBE KEYSPACE expansion_toolkit_test;"

 docker run --rm -t \
         -v ~/.aws:/root/.aws \
          amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
          --execute "CREATE TABLE expansion_toolkit_test.backofftest (
           id text,
           name text,
           description text,
           details map<text,text>,
           PRIMARY KEY(id, name))
           WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

docker run --rm -t \
           -v ~/.aws:/root/.aws \
           --entrypoint aws-cqlsh-expansion-expo-backoff.sh \
           amazon/amazon-keyspaces-toolkit  30 120 $HOST $PORT --ssl \
             --execute "DESCRIBE TABLE expansion_toolkit_test.backofftest;"

docker run --rm -t \
            -v ~/.aws:/root/.aws \
             amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
           --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO expansion_toolkit_test.backofftest(id, name, description, details) VALUES('1', 'abc', 'xyz', {'key1':'value1'});"

docker run --rm -t  \
           -v ~/.aws:/root/.aws \
            amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
          --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO expansion_toolkit_test.backofftest(id, name, description, details) VALUES('2', 'efg', 'hij', {'key2':'value2'}) IF NOT EXISTS;"

docker run --rm -t  \
           -v ~/.aws:/root/.aws \
            amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
            --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM expansion_toolkit_test.backofftest;"

docker run --rm -t  \
             -v ~/.aws:/root/.aws \
              amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
            --execute "CONSISTENCY LOCAL_QUORUM; COPY expansion_toolkit_test.backofftest TO 'data.csv';COPY expansion_toolkit_test.backofftest FROM 'data.csv';";

docker run --rm -t  \
               -v ~/.aws:/root/.aws \
               -v "$(pwd)":/source \
                amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
               --file /source/docker/test/test.cql

docker run --rm -t \
            -v ~/.aws:/root/.aws \
             amazon/amazon-keyspaces-toolkit $HOST $PORT --ssl \
             --execute "DROP KEYSPACE expansion_toolkit_test;"

echo "Finished sm helper tests with auth provider SigV4AuthProvider"
