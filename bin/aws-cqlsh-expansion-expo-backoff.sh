#!/bin/bash
#--------------------------------------------------------------------
#Description: exponential Backoff for CQL statements for Amazon Keyspaces
#author: Michael Raney
#date: 5/11/2020
#--------------------------------------------------------------------

#paramters
#$1 max time for program to run in seconds (example 360)
#$2 max number of attempts to run (example 100)
#$3 CQL Statment

#config
capbackoff=60   #max backoff time for request in seconds
basebackoff=5   #minimum backoff time for request in seconds
maxtime=600     #max time for program to run in seconds
maxattempts=100 #max number of attempts to run

#global varriables do not modify
attempts=1
success=1
backoff=0

trap "echo Exited!; exit;" SIGINT SIGTERM

echo "${@:3}"

while [ $success -ne 0 -a $attempts -le $2 -a $SECONDS -le $1 ]
 do

  echo "---------------------------"
  echo "attempt:        $attempts"
  echo "sleep:          $backoff seconds"
  sleep $backoff
  echo "total duration: $SECONDS seconds"
  echo ""

  #take paramters starting at $3
  cqlsh-expansion "${@:3}"

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
