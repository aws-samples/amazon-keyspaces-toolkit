#!/bin/bash

#Simple test for functionality of Keyspaces toolkit.

#arguments
SERVICEUSERNAME=$1
SERVICEPASSWORD=$2
SECRETKEY=$3
HOST=$4
PORT=$5

docker build --tag amazon/keyspaces-toolkit -f ../Dockerfile ../ --build-arg CLI_VERSION=latest

docker run --rm -t amazon/keyspaces-toolkit \
        $HOST $PORT \
        -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl \
        --execute "SHOW VERSION; SHOW HOST;"

docker run --rm -t amazon/keyspaces-toolkit \
    $HOST $PORT \
    -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl \
    --execute "CREATE KEYSPACE toolkit_test WITH
    REPLICATION = {'class': 'SingleRegionStrategy'};"

docker run --rm -t --entrypoint aws-cqlsh-expo-backoff.sh amazon/keyspaces-toolkit \
              30 120 \
              $HOST $PORT \
              --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
              --execute "DESCRIBE KEYSPACE toolkit_test;"


docker run --rm -t amazon/keyspaces-toolkit \
        $HOST $PORT \
        -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl \
        --execute "CREATE TABLE toolkit_test.backofftest(
         id text,
         name text,
         description text,
         PRIMARY KEY(id, name))
         WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

docker run --rm -t --entrypoint aws-cqlsh-expo-backoff.sh amazon/keyspaces-toolkit \
          30 360 \
          $HOST $PORT \
          --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
          --execute "DESCRIBE TABLE toolkit_test.backofftest;"

docker run --rm -t  amazon/keyspaces-toolkit \
          $HOST $PORT \
          --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
          --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO toolkit_test.backofftest(id, name, description) VALUES('1', 'abc', 'xyz');"

docker run --rm -t  amazon/keyspaces-toolkit \
                    $HOST $PORT \
                    --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
                    --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO toolkit_test.backofftest(id, name, description) VALUES('2', 'efg', 'hij') IF NOT EXISTS;"


docker run --rm -t  amazon/keyspaces-toolkit \
            $HOST $PORT \
            --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
            --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM toolkit_test.backofftest;"

docker run --rm -t  amazon/keyspaces-toolkit \
                $HOST $PORT \
                --ssl -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" \
                --execute "CONSISTENCY LOCAL_QUORUM; COPY toolkit_test.backofftest TO 'data.csv';COPY toolkit_test.backofftest FROM 'data.csv';";

docker run --rm -t amazon/keyspaces-toolkit \
              $HOST $PORT \
              -u "$SERVICEUSERNAME" -p "$SERVICEPASSWORD" --ssl \
              --execute "DROP KEYSPACE toolkit_test;"

#secrets manager helper
echo "secrets manager helper tests"
docker run --rm -t \
    -v ~/.aws:/root/.aws \
    --entrypoint aws-sm-cqlsh.sh \
     amazon/keyspaces-toolkit $SECRETKEY \
    $HOST $PORT --ssl \
    --execute "CREATE KEYSPACE sm_toolkit_test WITH
 REPLICATION = {'class': 'SingleRegionStrategy'};"

 docker run --rm -t \
    -v ~/.aws:/root/.aws \
    --entrypoint aws-sm-cqlsh-expo-backoff.sh \
    amazon/keyspaces-toolkit $SECRETKEY 30 120 \
     $HOST $PORT --ssl \
     --execute "DESCRIBE KEYSPACE sm_toolkit_test;"

 docker run --rm -t \
         -v ~/.aws:/root/.aws \
         --entrypoint aws-sm-cqlsh.sh \
          amazon/keyspaces-toolkit $SECRETKEY $HOST $PORT --ssl \
          --execute "CREATE TABLE sm_toolkit_test.backofftest (
           id text,
           name text,
           description text,
           PRIMARY KEY(id, name))
           WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}};"

docker run --rm -t \
           -v ~/.aws:/root/.aws \
           --entrypoint aws-sm-cqlsh-expo-backoff.sh \
           amazon/keyspaces-toolkit $SECRETKEY 30 120 $HOST $PORT --ssl \
             --execute "DESCRIBE TABLE sm_toolkit_test.backofftest;"

docker run --rm -t \
            -v ~/.aws:/root/.aws \
            --entrypoint aws-sm-cqlsh.sh \
            amazon/keyspaces-toolkit $SECRETKEY $HOST $PORT --ssl \
           --execute "CONSISTENCY LOCAL_QUORUM; INSERT INTO sm_toolkit_test.backofftest(id, name, description) VALUES('1', 'abc', 'xyz');"

docker run --rm -t  \
           -v ~/.aws:/root/.aws \
           --entrypoint  aws-sm-cqlsh.sh \
           amazon/keyspaces-toolkit $SECRETKEY $HOST $PORT --ssl \
          --execute "CONSISTENCY LOCAL_QUORUM; SERIAL CONSISTENCY LOCAL_SERIAL; INSERT INTO sm_toolkit_test.backofftest(id, name, description) VALUES('2', 'efg', 'hij') IF NOT EXISTS;"

docker run --rm -t  \
           -v ~/.aws:/root/.aws \
           --entrypoint aws-sm-cqlsh.sh \
           amazon/keyspaces-toolkit $SECRETKEY $HOST $PORT --ssl \
            --execute "CONSISTENCY LOCAL_QUORUM; SELECT * FROM sm_toolkit_test.backofftest;"

docker run --rm -t  \
             -v ~/.aws:/root/.aws \
             --entrypoint  aws-sm-cqlsh.sh \
             amazon/keyspaces-toolkit $SECRETKEY $HOST $PORT --ssl \
            --execute "CONSISTENCY LOCAL_QUORUM; COPY sm_toolkit_test.backofftest TO 'data.csv';COPY sm_toolkit_test.backofftest FROM 'data.csv';";

 docker run --rm -t \
 -v ~/.aws:/root/.aws \
 --entrypoint aws-sm-cqlsh.sh \
  amazon/keyspaces-toolkit $SECRETKEY \
  $HOST $PORT --ssl \
  --execute "DROP KEYSPACE sm_toolkit_test;"
