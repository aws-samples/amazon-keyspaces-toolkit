#!/bin/bash
#--------------------------------------------------------------------
#Description: exponential Backoff for CQL statements for Amazon Keyspaces
#author: Michael Raney
#date: 5/11/2020
#--------------------------------------------------------------------

#paramters
#$1 aws secret key to retrieve credentials from Amazon Secrets Manager
#$2 max time for program to run in seconds (example 360)
#$3 max number of attempts to run (example 100)
#$4 CQL Statment

#config
capbackoff=60   #max backoff time for request in seconds
basebackoff=5   #minimum backoff time for request in seconds


#global varriables do not modify
attempts=1
success=1
backoff=0

trap "echo Exited!; exit;" SIGINT SIGTERM

mysecret=$(aws secretsmanager get-secret-value --secret-id "$1" --region "$4" --query SecretString --output text)

username=$(jq --raw-output '.username' <<< $mysecret)
password=$(jq --raw-output '.password' <<< $mysecret)
host=$(jq --raw-output '.host' <<< $mysecret)
port=$(jq --raw-output '.port' <<< $mysecret)

echo "cqlsh-expansion $host $port -u **** -p **** ${@:5}"

while [ $success -ne 0 -a $attempts -le $3 -a $SECONDS -le $2  ]
 do

  echo "---------------------------"
  echo "attempt:        $attempts"
  echo "sleep:          $backoff seconds"
  sleep $backoff
  echo "total duration: $SECONDS seconds"
  echo ""

  #take paramters starting at $4
  cqlsh-expansion $host $port -u $username -p $password "${@:5}"

  success=$?
 ((attempts++))

  #based on exponential backoff with jitter blog
  #https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter
  backoff=$((basebackoff + (RANDOM % ((1 + (backoff * 3))))))

  if [ "$backoff" -gt "$capbackoff" ]
  then
    backoff=$capbackoff
  fi

done

echo "Finished final exit code: $?"
